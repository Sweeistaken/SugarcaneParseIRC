import socket
class message: # Message object
    def __init__(self, content:str, channel:str, nick:str):
        self.content = content
        self.channel = channel
        self.nick = nick
class channel: # Channel object
    is_init = False
    topic = ""
    modes = "+nt"
    def __init__(self, name:str):
        self.name = name
    def info_set(self, topic:str, modes:str): # Socket will automatically initialize the channel object
        self.is_init = True
        self.topic, self.modes = topic, modes
class IRCSession: # Actual IRC session
    messages = None # Cached messages
    connecting = False # Connection status
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket
    def __init__(self, address:str, port:int, nick:str, user:str, *args, **kwargs): # Contains the configuration
        self.server, self.port, self.nick, self.user = address,port,nick,user
    def connect(self): # Attempt to connect
        print("Connecting to " + self.server + ":" + str(self.port) + "...")
        self.socket.connect((self.server, self.port))
        self.connecting = True
        return False
    def alive(self): # NOT FINISHED: To minimize exceptions, the client can ask the object if the socket connection is still alive.
        return False
    def whois(self, nick:str): # NOT FINISHED: Try to /whois the user, will return a user() object or None.
        return None