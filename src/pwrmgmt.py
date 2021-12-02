import RPi.GPIO as GPIO
import threading
import time
import socket
import subprocess
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

LEDPWR_PIN_OUT = 3   # LED power relay control
LINEPWR_PIN_IN = 4   # LINEPWR (5v wall power) sensing
# PWR_EN_PIN_OUT = 14  # PowerBoost Enable -- Using UART Signal

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ("/RPC2",)

class PowerManagementServer(SimpleXMLRPCServer):
    def __init__(self):
        super().__init__(("0.0.0.0", 8000), requestHandler=RequestHandler)
        self.gpio_running = True
        GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme

        # Configure external power sensing pin
        GPIO.setup(LINEPWR_PIN_IN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.sense_ext_pwr_running = True
        self.sense_ext_pwr_thread = threading.Thread(target=self._sense_ext_pwr)
        self.sense_ext_pwr_thread.start()

        # Configure LED Power Relay Control pin
        GPIO.setup(LEDPWR_PIN_OUT, GPIO.OUT)
        self.led_power_enabled = True  # True: GPIO.HIGH,  False: GPIO.LOW


        # Register XMLRPC Services
        self.serve_forever_running = True
        self.register_introspection_functions()
        self.register_function(self.led_power)

    def serve_forever(self):
        """ Overrides built-in SimpleXMLRPCServer.serve_forever() 
        Handles incomming XMLRPC requests, but allows for graceful shutdown of process 
        """
        print("PowerManagement: serve_forever() Starting")
        try:
            while self.serve_forever_running:
                print("PowerManagement: serve_forever() Waiting for request")
                # handle_request() blocks until it receives a request (or ctrl-c).
                self.handle_request()
        except KeyboardInterrupt:
            print("PowerManagement: serve_forever() Caught Kill Signal")
            self.serve_forever_running = False
            # Signal Power Sensing thread to shut down
            self.sense_ext_pwr_running = False
            time.sleep(1)
            # Wait for external power sensing thread
            self.sense_ext_pwr_thread.join()
            self._shutdown_service()

        print("PowerManagement: serve_forever() Exiting")

    def _sense_ext_pwr(self):
        """ Run as a thread, checks for the presence of external power """
        print("PowerManagement: sense_ext_pwr() starting")
        time.sleep(0.5)
        try:
            while self.sense_ext_pwr_running:
                if not GPIO.input(LINEPWR_PIN_IN):
                    print("PowerManagement: sense_ext_pwr() Power Loss Detected - Shutting down!")
#                     subprocess.call(["shutdown", "-h", "now"])
                    self.sense_ext_pwr_running = False
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("PowerManagement: sense_ext_pwr() Caught Kill Signal")
            self.sense_ext_pwr_running = False

        # Begin Service Shutdown
        # If serve_forever() is still running, shut it down
        if self.serve_forever_running:
            self.serve_forever_running = False
            # Attempt to unblock serve_forever() by making xmlrpc call
            print("PowerManagement: sense_ext_pwr() xmlrpc - calling server")
            try:
                proxy = xmlrpc.client.ServerProxy("http://localhost:8000/RPC2")
                socket.setdefaulttimeout(1)
                proxy.system.listMethods()
                print("PowerManagement: sense_ext_pwr() xmlrpc - success")
            except socket.timeout:
                print("PowerManagement: sense_ext_pwr() xmlrpc - FAILURE")
            finally:
                socket.setdefaulttimeout(None)

        print("PowerManagement: sense_ext_pwr() exiting")
        self._shutdown_service()


    def led_power(self, enable):
        """ Enable or disable LED Power Relay (xmlrpc service) """
        if enable:
            print("PowerManagement: led_power() Enable")
            GPIO.output(LEDPWR_PIN_OUT, GPIO.HIGH)
        else:
            print("PowerManagement: led_power() Disable")
            GPIO.output(LEDPWR_PIN_OUT, GPIO.LOW)
        self.led_power_enabled = enable
        time.sleep(0.1)
        return True

    def _shutdown_service(self):
        if self.gpio_running:
            print("PowerManagement: GPIO Cleanup Starting")
            GPIO.cleanup()
            self.gpio_running = False
            print("PowerManagement: GPIO Cleanup Complete")


# def relay_test():
#     GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
#     GPIO.setup(LEDPWR_PIN_OUT, GPIO.OUT)
#     print("Relay Off")
#     GPIO.output(LEDPWR_PIN_OUT, GPIO.LOW)
#     try:
#         while 1:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         pass
#     print("Relay On")
#     GPIO.output(LEDPWR_PIN_OUT, GPIO.HIGH)
#     time.sleep(1)
#     GPIO.cleanup()


def main():
    pwr_mgmt = PowerManagementServer()
    pwr_mgmt.led_power(False)
    pwr_mgmt.serve_forever()
    print("main() Exiting")

if __name__ == "__main__":
    main()

