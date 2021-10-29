from xmlrpc.client import ServerProxy

def stop_lights():
    server = ServerProxy("http://lowerledcontroller.danland.net:9000/RPC2")
    proc_info = server.supervisor.getProcessInfo("lights")
    print(proc_info['statename'])
    if proc_info["statename"] == "RUNNING":
        print("Turning off Lights")
        try:
            return server.supervisor.stopProcess("lights")
        except xmlrpc.client.Fault:
            print("Command Failed")
            return False

if __name__ == "__main__":
    stop_lights()
