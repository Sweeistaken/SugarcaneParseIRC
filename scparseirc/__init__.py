"""
IRC Parser for the SugarCaneIRC family.
"""
import socket
import ssl as ssl_module
class message: # Message object
    def __init__(self, content:str, channel:str, nick:str):
        self.content = content
        self.channel = channel
        self.nick = nick
class channel: # Channel object
    is_init = False # If the channel's properties are initialized yet
    topic = "" # Channel topic
    modes = "+nt" # Channel modes
    def __init__(self, name:str):
        self.name = name
    def info_set(self, topic:str, modes:str): # Socket will automatically initialize the channel object
        self.is_init = True
        self.topic, self.modes = topic, modes
class IRCSession: # Actual IRC session
    messages = None # Cached messages
    connecting = False # Connection status
    is_ssl = False # Wether the connection uses TLS/SSL
    ssl_accept_invalid = False # If SSL is enabled, do not fail to connect if the certificate is invalid.
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket
    wsocket = None # Wrapped socket (if SSL is enabled)
    context = ssl_module.create_default_context()
    def __init__(self, address:str, port:int, nick:str, user:str, ssl:bool, ssl_igninvalid:bool, *args, **kwargs): # Contains the configuration
        self.server, self.port, self.nick, self.user, self.ssl, self.ssl_accept_invalid = address,port,nick,user,ssl,ssl_igninvalid
        if ssl:
            self.wsocket = self.context.wrap_socket(self.socket, server_hostname=address)
            if ssl_igninvalid:
                self.context = ssl_module._create_unverified_context()
    def connect(self): # Attempt to connect
        print("Connecting to " + self.server + ":" + str(self.port) + "...")
        if self.ssl:
            self.wsocket.connect((self.server, self.port))
        else:
            self.socket.connect((self.server, self.port))
        self.connecting = True
        return False
    def alive(self): # NOT FINISHED: To minimize exceptions, the client can ask the object if the socket connection is still alive.
        return False
    def whois(self, nick:str): # NOT FINISHED: Try to /whois the user, will return a user() object or None.
        return None