from xmlrpc.client import ServerProxy

def start_lights():
    server = ServerProxy("http://localhost:80/RPC2")
    proc_info = server.supervisor.getProcessInfo("lights")
    print(proc_info['statename'])
    if proc_info["statename"] != "RUNNING":
        print("Turning on Lights")
        try:
            return server.supervisor.startProcess("lights")
        except xmlrpc.client.Fault:
            print("Command Failed")
            return False

if __name__ == "__main__":
    start_lights()
