try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    print("WARNING: Could NOT Import GPIO, using Fake")
    class GPIO(object):
        def setmode(self, arg1):
            pass
        def setup(self, arg1, arg2):
            pass
        def cleanup(self):
            pass
        def output(self, arg1, arg2):
            pass

import socket
import time
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

LEDPWR_PIN_OUT = 3   # LED power relay control

class LEDPowerClient(object):
    """ Client for LED Power management
    from ledpower_service import LEDPowerClient
    power = LEDPowerClient()
    power.enable()
    power.disable()
    """
    def __init__(self):
        self.led_power_proxy = xmlrpc.client.ServerProxy("http://localhost:8000/RPC2")

    def _call_led_power_service(self, value):
        """ Calls the remote procedure"""
        assert(isinstance(value, bool))
        socket.setdefaulttimeout(1)
        try:
            ret = self.led_power_proxy.enable_led_power(value) # Should return True
        except socket.timeout:
            print("WARNING: LEDPowerClient() Timeout waiting for reply")
            ret = False
        except ConnectionRefusedError:
            print("WARNING: LEDPowerClient() Unable to connect to server")
            ret = False
        socket.setdefaulttimeout(None)
        return ret

    def enable(self):
        """ Enable LED Power """
        return self._call_led_power_service(True)

    def disable(self):
        """ Disable LED Power """
        return self._call_led_power_service(False)

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ("/RPC2",)

class LEDPowerManagementServer(SimpleXMLRPCServer):
    def __init__(self):
        super().__init__(("0.0.0.0", 8000), requestHandler=RequestHandler)
        # Configure LED Power Relay Control pin
        GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
        GPIO.setup(LEDPWR_PIN_OUT, GPIO.OUT)

        # Register XMLRPC Services
        self.running = True
        self.register_introspection_functions()
        self.register_function(self.enable_led_power)

    def serve_forever(self):
        """ Overrides built-in SimpleXMLRPCServer.serve_forever() 
        Handles incomming XMLRPC requests, but allows for graceful shutdown of process 
        """
        print("LEDPowerManagement: serve_forever() Starting")
        try:
            while self.running:
                # handle_request() blocks until it receives a request (or ctrl-c).
                self.handle_request()
        except KeyboardInterrupt:
            print("LEDPowerManagement: serve_forever() Caught Kill Signal")
            self.running = False
        print("LEDPowerManagement: GPIO Cleanup")
        GPIO.cleanup()
        print("LEDPowerManagement: serve_forever() Exiting")

    def enable_led_power(self, enable):
        """ Enable or disable LED Power Relay (xmlrpc service)
        True: GPIO.HIGH,  False: GPIO.LOW
        """
        if enable:
            print("LEDPowerManagement: led_power() Enable")
            GPIO.output(LEDPWR_PIN_OUT, GPIO.HIGH)
        else:
            print("LEDPowerManagement: led_power() Disable")
            GPIO.output(LEDPWR_PIN_OUT, GPIO.LOW)
        time.sleep(0.1)
        return True


def main():
    pwr_mgmt = LEDPowerManagementServer()
    pwr_mgmt.enable_led_power(False)
    pwr_mgmt.serve_forever()
    print("main() Exiting")

if __name__ == "__main__":
    main()

