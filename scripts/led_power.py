import argparse
from xmlrpc.client import ServerProxy

def led_power_control(args):
    server = ServerProxy("http://localhost:8000/RPC2")
    try:
        state = True if args.action == "enable" else False
        server.led_power(state)
    except xmlrpc.client.Fault:
        print("Command Failed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LED Power Relay Control")
    parser.add_argument('action', choices=["enable", "disable"])
    args = parser.parse_args()
    led_power_control(args)
