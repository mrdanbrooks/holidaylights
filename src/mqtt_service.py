import configparser
import os
import socket # For gethostname()
import time
import threading  # for Timer()
import paho.mqtt.client as mqtt
import http  # For CannotSendRequest
from  xmlrpc.client import ServerProxy

from timer import Timer

TOPIC_PREFIX = "smartlights/"
STATUS_UPDATE_RATE = 5
PAYLOAD_ON = "ON"
PAYLOAD_OFF = "OFF"
AVAILABLE = "online"
UNAVAILABLE = "offline"
STATE_ON = "ON"
STATE_OFF = "OFF"

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# client = MQTTClient(127.0.0.1, 1883, "nodename", "username", "password")
# client.add_subscriber(topic, callback_fun)
# client.start()
# client.publish(topic, data)
# client.stop()

class MQTTClient(object):
    def __init__(self, broker, port, clientid, username, password):
        self._mqttc = mqtt.Client(clientid)
        self._mqttc.username_pw_set(username, password)

        # Setup MQTT Callbacks
        self._mqttc.on_connect = self._on_connect
        self._mqttc.on_disconnect = self._on_disconnect
        self._mqttc.on_message = self._on_message

        self._broker = broker
        self._port = port

        # Setup Subscription Callbacks
        self._subscriptions = dict() # topic: callback_fun
        self.connected=False

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("MQTTClient: Connected")
            self.connected=True
            # On connection or reconnection, attach subscriptions
            for topic in self._subscriptions.keys():
                self._mqttc.subscribe(topic, qos=2)
        else:
            print("MQTTClient: Failed to connect, return code %d" % rc)

    def _on_disconnect(self, client, userdata, rc):
        print("MQTTClient: disconnected" % (client, rc))
        self.connected=False

    def _on_message(self, client, userdata, msg):
        # print("Received:" + msg.topic + ": " + str(msg.payload))
        self._subscriptions[msg.topic](msg.topic, msg.payload)

    def start(self):
        """ start background looping thread """
        # Use connect_async() instead of connect() so that the command does not fail if 
        # there is no immediate connection to the broker
        self._mqttc.connect_async(self._broker, self._port, keepalive=3)
        # Start background publish / subscribe socket connections
        self._mqttc.loop_start()

    def stop(self):
        """ ends background looping thread """
        self._mqttc.loop_stop()

    def subscribe(self, topic, callback_fun): 
        """
        callbackfun(topic, data)
        """
        if topic in self._subscriptions.keys():
            raise Error("MQTTClient: Topic %s already subscribed" % topic)
        self._subscriptions[topic] = callback_fun

    def publish(self, topic, value):
        self._mqttc.publish(topic, value, qos=2, retain=True)

def test_mqttclient():
    def printer(topic, data):
        print("here is %s" % data)

    config = configparser.ConfigParser()
    config.read_file(open(os.path.join(SCRIPT_DIR,"mqtt.conf")))
    broker = config["mqtt"]["broker"]
    port = int(config["mqtt"]["port"])
    user = config["mqtt"]["user"]
    password = config["mqtt"]["password"]

    client = MQTTClient(broker, 
                        port, 
                        "testclient", 
                        user, 
                        password)
    client.subscribe("test/dan", printer)
    client.start()
    val = 0
    try:
        while True:
            val += 1
            client.publish("test/dan", val)
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        client.stop()

class MQTTSwitchService(object):
    def __init__(self, broker, port, user, password):
        self.hostname = socket.gethostname()

        # Setup XMLRPC connection to Supervisor
        self.supervisor_client = ServerProxy("http://localhost:80/RPC2")
    
        # Setup MQTT connection to Home Assistant
        self.mqtt_client = MQTTClient(broker, port, self.hostname, user, password)
        self.mqtt_client.subscribe(TOPIC_PREFIX + self.hostname + "/set", self._set_callback)
        self.state_topic = TOPIC_PREFIX + self.hostname
        self.availability_topic = TOPIC_PREFIX + self.hostname + "/available"

        # Setup MQTT publishing timer
        self.publish_update_timer = Timer(STATUS_UPDATE_RATE, self._publish_update)
        self.publish_update_timer.start()

    def _set_callback(self, topic, data):
        """ called when .../set receives data to turn switch on or off """
        try:
            if data.decode('utf-8') == PAYLOAD_ON:
                print("Requesting Supervisor lights ON")
                # Stop the updater from sending while we are changing process state
                print("Cancel updater")
                self.publish_update_timer.cancel()
                # Send anticipated state back
                print("Send State ON")
                self.mqtt_client.publish(self.state_topic, PAYLOAD_ON)
                time.sleep(0.5)
                # Call Process to Start - this might take a while
                # TODO: This needs to happen in a thread because it is causing
                # the callback to take too long, and switch on the server is not responding
                self.supervisor_client.supervisor.startProcess("lights")
            elif data.decode('utf-8') == PAYLOAD_OFF:
                print("Requesting Supervisor lights OFF")
                # Stop the updater from sending while we are changing process state
                self.publish_update_timer.cancel()
                # Send anticipated state back
                print("Send State OFF")
                self.mqtt_client.publish(self.state_topic, PAYLOAD_OFF)
                # Call Process to Stop - this might take a while
                self.supervisor_client.supervisor.stopProcess("lights")
            else:
                print("ERROR: Did not understand payload '%s'" % data)
        except socket.timeout:
            print("WARNING: LEDPowerClient() Timeout waiting for reply")
        except ConnectionRefusedError:
            print("WARNING: LEDPowerClient() Unable to connect to server")
        except http.client.CannotSendRequest:
            print("WARNING: LEDPowerClient() Cannot send xmlrpc request to server")
        except:
            print("ERROR: caught XMLRPC ERROR - investigate")
        finally:
            # Immediately query and publish new state
            print("Publish update")
            self._publish_update()
            # restart the update timer
            print("Restart timer")
            self.publish_update_timer.start()
 
    def _publish_update(self):
        """  Sends updates about the device status
        called by publish_update_timer
        """
        print("Retreiving supervisor status")
        try:
            proc_info = self.supervisor_client.supervisor.getProcessInfo("lights")
        except socket.timeout:
            print("WARNING: LEDPowerClient() Timeout waiting for reply")
            proc_info = False
        except ConnectionRefusedError:
            print("WARNING: LEDPowerClient() Unable to connect to server")
            proc_info = False
        except http.client.CannotSendRequest:
            print("WARNING: LEDPowerClient() Cannot send xmlrpc request to server")
            proc_info = False
        except:
            print("ERROR: caught XMLRPC ERROR - investigate")
            proc_info = False
        
        
        if not proc_info:
            # If XMLRPC is not available, list device as unavailable
            self.mqtt_client.publish(self.availability_topic, UNAVAILABLE)
            return

        # Received Data. publish it
        self.mqtt_client.publish(self.availability_topic, AVAILABLE)
        if proc_info["statename"] != "RUNNING":
            data = PAYLOAD_OFF
            print("supervisor status: OFF")
        else:
            data = PAYLOAD_ON
            print("supervisor status: ON")
        self.mqtt_client.publish(self.state_topic, data)


    def run(self):
        self.mqtt_client.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.publish_update_timer.cancel()
            self.mqtt_client.stop()

def main():
    config = configparser.ConfigParser()
    config.read_file(open(os.path.join(SCRIPT_DIR,"mqtt.conf")))
    broker = config["mqtt"]["broker"]
    port = int(config["mqtt"]["port"])
    user = config["mqtt"]["user"]
    password = config["mqtt"]["password"]
    client = MQTTSwitchService(broker, port, user, password)
    client.run()

if __name__ == "__main__":
    #test_mqttclient()
    main()



