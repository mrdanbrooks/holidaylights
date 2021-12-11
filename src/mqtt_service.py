#
# mqtt_service.py
# [db] 2021-12-10
# 
# Exposes Supervisord control of 'lights' process to Home Assistant over MQTT
#
# PREREQUESITES:
# - Make sure MQTT Mosquitto broker is installed and configured on Home Assistant
#
# INSTALL
# 1) Edit mqtt.conf
# 2) Make sure git does not try to save your secrets
#    git update-index --assume-unchanged src/mqtt.conf
# 3) install dependencies and service by running
#    ./scripts/install_mqtt_service.sh
# 4) Edit Home Assistant configuration.yaml
#     switch:
#       - platform: mqtt
#         unique_id: <hostname>
#         name: "Upper LEDs"
#         state_topic: "smartlights/<hostname>"
#         command_topic: "smartlights/<hostname>/set"
#         availability:
#           - topic: "smartlights/<hostname>/available"
#         payload_on: "ON"
#         payload_off: "OFF"
#         state_on: "ON"
#         state_off: "OFF"

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
    """ Example of how to use MQTTClient without additional XMLRPC code """
    def printer(topic, data):
        print("here is %s" % data)

    # Don't store credentials in code
    config = configparser.ConfigParser()
    config.read_file(open(os.path.join(SCRIPT_DIR,"mqtt.conf")))
    broker = config["mqtt"]["broker"]
    port = int(config["mqtt"]["port"])
    user = config["mqtt"]["user"]
    password = config["mqtt"]["password"]

    # Client setup
    client = MQTTClient(broker, port, "testclient", user, password)
    client.subscribe("test/dan", printer)

    # Start Client
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
        # Stop Client
        client.stop()





class MQTTSwitchService(object):
    def __init__(self, broker, port, user, password):
        self.hostname = socket.gethostname()

        # Setup XMLRPC connection to Supervisor
        self.supervisor_client = ServerProxy("http://localhost:80/RPC2")
    
        # Setup MQTT connection to Home Assistant
        self.mqtt_client = MQTTClient(broker, port, self.hostname, user, password)
        self.mqtt_client.subscribe(TOPIC_PREFIX + self.hostname + "/set", self._set_state_callback)
        self.state_topic = TOPIC_PREFIX + self.hostname
        self.availability_topic = TOPIC_PREFIX + self.hostname + "/available"

        # Setup MQTT publishing timer
        self.xmlrpc_update_timer = Timer(STATUS_UPDATE_RATE, self._xmlrpc_update)

        # XMLRPC Commands getting process info are pretty fast, but startProcesss() and stopProcess()
        # can take a long time to return. This results in HomeAssistant switches flip/flopping back
        # to their previous state when they fail to get a quick update that state has successfully changed.
        # We will assume process control calls succeed and send the expected state back to HA, then run the actual
        # XMLRPC commands to set process control in a seperate thread. If the process control fails,
        # this will be caught by the periodic xmlrpc_update_timer which will detect the actual process
        # state and send a corrected state to HA.
        self._xmlrpc_cmd_queue = list()

    def _set_state_callback(self, topic, data):
        """ called when .../set receives data to turn switch on or off """
        if data.decode('utf-8') == PAYLOAD_ON:
            print("Requesting Supervisor lights ON")
            # Send anticipated state back
            self.mqtt_client.publish(self.state_topic, PAYLOAD_ON)
            # Add PAYLOAD_ON to xmlrpc queue
            self._xmlrpc_cmd_queue.append(PAYLOAD_ON)
            # Immediately run xmlrpc update
            self.xmlrpc_update_timer.fire_and_restart()
        elif data.decode('utf-8') == PAYLOAD_OFF:
            print("Requesting Supervisor lights OFF")
            # Send anticipated state back
            self.mqtt_client.publish(self.state_topic, PAYLOAD_OFF)
            # Add PAYLOAD_OFF to xmlrpc queue
            self._xmlrpc_cmd_queue.append(PAYLOAD_OFF)
            # Immediately run xmlrpc update
            self.xmlrpc_update_timer.fire_and_restart()
        else:
            print("ERROR: Did not understand payload '%s'" % data)


    def _xmlrpc_update(self): 
        """  Makes long running XMLRPC commands and sends updates about the device status back on MQTT """
        # Check if there are process control commands to run
        while self._xmlrpc_cmd_queue:
            cmd = self._xmlrpc_cmd_queue.pop(0)
            try:
                if cmd == PAYLOAD_ON:
                    # Call Process to Start - this might take a while
                    self.supervisor_client.supervisor.startProcess("lights")
                elif cmd == PAYLOAD_OFF:
                    # Call Process to Stop - this might take a while
                    self.supervisor_client.supervisor.stopProcess("lights")
            except (socket.timeout, ConnectionRefusedError, http.client.CannotSendRequest) as e:
                print("WARNING: %s" % str(e))
            except Exception as e:
                print("ERROR: %s while calling XMLRPC - investigate" % str(e))


        # Check process state using XMLRPC and send Home Assistant update over MQTT
        proc_info = False
        try:
            proc_info = self.supervisor_client.supervisor.getProcessInfo("lights")
        except (socket.timeout, ConnectionRefusedError, http.client.CannotSendRequest) as e:
            print("WARNING: %s" % str(e))
        except Exception as e:
            print("ERROR: %s while calling XMLRPC - investigate" % str(e))

        if not proc_info:
            # If XMLRPC is not available, list device as unavailable
            self.mqtt_client.publish(self.availability_topic, UNAVAILABLE)
            return

        # Received Data. publish it
        self.mqtt_client.publish(self.availability_topic, AVAILABLE)
        if proc_info["statename"] != "RUNNING":
            data = PAYLOAD_OFF
        else:
            data = PAYLOAD_ON
        self.mqtt_client.publish(self.state_topic, data)


    def run(self):
        """ Main Service Loop """
        self.xmlrpc_update_timer.start()
        self.mqtt_client.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.xmlrpc_update_timer.cancel()
            self.mqtt_client.stop()

def main():
    # Read Credentials
    config = configparser.ConfigParser()
    config.read_file(open(os.path.join(SCRIPT_DIR,"mqtt.conf")))
    broker = config["mqtt"]["broker"]
    port = int(config["mqtt"]["port"])
    user = config["mqtt"]["user"]
    password = config["mqtt"]["password"]

    # Run Service
    client = MQTTSwitchService(broker, port, user, password)
    client.run()

if __name__ == "__main__":
    #test_mqttclient()
    main()



