"""
IRC Parser for the SugarCaneIRC family.
"""
import socket
import ssl as ssl_module
import threading
class systemMessage: # System message object
    chan = None
    def __init__(self, content:str, user:str, typ:str, mention:bool, **kwargs):
        self.content, self.user, self.type, self.mention = content,user,typ,mention
        if "chan" in kwargs:
            self.chan = kwargs["chan"]
class message: # Message object
    def __init__(self, content:str, chan:str, nick:str):
        self.content = content
        self.channel = chan
        self.nick = nick
class channel: # Channel object
    is_init = False # If the channel's properties are initialized yet
    topic = "" # Channel topic
    modes = "+nt" # Channel modes
    in_channel = True # If the user is in the channel
    def __init__(self, name:str):
        self.name = name
    def info_set(self, topic:str, modes:str): # Socket will automatically initialize the channel object
        self.is_init = True
        self.topic, self.modes = topic, modes
class IRCSession: # Actual IRC session
    messages = [] # Cached messages
    raw_text = "" # Cached RAW data
    channels = [] # Cached channels
    connecting = False # Connection status
    is_ssl = False # Wether the connection uses TLS/SSL
    ssl_accept_invalid = False # If SSL is enabled, do not fail to connect if the certificate is invalid.
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket
    wsocket = None # Wrapped socket (if SSL is enabled)
    context = ssl_module.create_default_context() # Context of the SSL module, not to be changed by the client.
    def __init__(self, address:str, port:int, nick:str, user:str, ssl:bool, ssl_igninvalid:bool, **kwargs): # Contains the configuration
        self.server, self.port, self.nick, self.user, self.ssl, self.ssl_accept_invalid = address,port,nick,user,ssl,ssl_igninvalid
        if ssl:
            if ssl_igninvalid:
                self.context = ssl_module._create_unverified_context()
            self.wsocket = self.context.wrap_socket(self.socket, server_hostname=address)
    def connect(self): # Attempt to connect
        print("Connecting to " + self.server + ":" + str(self.port) + "...")
        if self.ssl:
            self.wsocket.connect((self.server, self.port))
        else:
            self.socket.connect((self.server, self.port))
        self.connecting = True
        return False
    def get(self): # Attempt to get the raw data and parse it.
        # The code is copied from sweeBotIRC btw
        r = self.socket.recv().recv(2040).decode()
        self.raw_text += r
        self.parseall()
        print(r)
        if r.find("PING") != -1:
            self.irc_socket.send(
                bytes("PONG " + r.split()[1] + "\r\n", "UTF-8")
            )
    def parseall(self): # Parse all of the fetched raw data, in a thread.
        threading.Thread(target=self.parse, kwargs={"content": self.raw_text})
    def parse(self, content:str):
        for i in content.replace("\r\n", "\n").split("\n"):
            pass
    def alive(self): # NOT FINISHED: To minimize exceptions, the client can ask the object if the socket connection is still alive.
        return False
    def whois(self, nick:str): # NOT FINISHED: Try to /whois the user, will return a user() object or None.
        return None