"""
IRC Parser for the SugarCaneIRC family.
"""
import socket
import ssl as ssl_module
import threading
__version__ = 0
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
    chans = [] # Cached channels
    connected = False # Connection status
    is_ssl = False # Wether the connection uses TLS/SSL
    ssl_accept_invalid = False # If SSL is enabled, do not fail to connect if the certificate is invalid.
    socket = socket.socket() # Socket
    wsocket = None # Wrapped socket (if SSL is enabled)
    context = ssl_module.create_default_context() # Context of the SSL module, not to be changed by the client.
    def __init__(self, address:str="irc.libera.chat", port:int=6697, nick:str="sweetAsSugar", user:str="ScParseIRC", ssl:bool=True, ssl_igninvalid:bool=False, realname:str="SugarcaneParseIRC user", **kwargs): # Contains the configuration
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.context = ssl_module.create_default_context()
        self.wsocket = None
        self.server, self.port, self.nick, self.user, self.ssl, self.ssl_accept_invalid, self.realname = address,port,nick,user,ssl,ssl_igninvalid,realname
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
        self.connected = True
        self.send("USER " + self.user + " " + self.user + " " + self.nick + " :SugarCaneIRC user\n")
        self.send(f"NICK {self.nick}\n")
    def send(self, content:str): # Attempt to send raw data to the socket
        if content[len(content)-1] != "\n":
            content+="\n"
        if self.ssl:
            self.wsocket.send(bytes(content,"UTF-8"))
        else:
            self.socket.send(bytes(content,"UTF-8"))
    def quit(self, message:str=f"ScParseIRC v{__version__}"):
        self.send(f"QUIT :" + message + "\n")
        self.connected = False
    def join(self, chan):
        self.chans.append(channel(chan))
        self.send(f"JOIN {chan}")
    def close(self):
        if self.ssl:
            self.wsocket.close()
        else:
            self.socket.close()
        self.connected = False
    def get(self): # Attempt to get the raw data and parse it.
        # The code is copied from sweeBotIRC btw
        if self.ssl:
            r = self.wsocket.recv(2040).decode()
        else:
            r = self.socket.recv(2040).decode()
        self.raw_text += r
        self.parseall()
        print(r)
        if r.find("PING") != -1:
            self.send(
               "PONG " + r.split()[1] + "\r\n"
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