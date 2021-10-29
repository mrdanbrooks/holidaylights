from xmlrpc.client import ServerProxy

def toggle_lights():
    server = ServerProxy("http://lowerledcontroller.danland.net:9000/RPC2")
    proc_info = server.supervisor.getProcessInfo("lights")
    print(proc_info['statename'])
    if proc_info["statename"] == "RUNNING":
        print("Turning Off Lights")
        try:
            return server.supervisor.stopProcess("lights")
        except xmlrpc.client.Fault:
            print("Command Failed")
            return False
    else:
        print("Turning On Lights")
        try:
            return server.supervisor.startProcess("lights")
        except xmlrpc.client.Fault:
            print("Command Failed")
            return False

toggle_lights()
