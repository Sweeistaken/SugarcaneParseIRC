"""
IRC Parser for the SugarCaneIRC family.
"""
import socket
import ssl as ssl_module
import threading
__version__ = "_TEST_"
class SystemMessage: # System message object
    def __init__(self, content:str, user:str, typ:str, mention:bool, chan:str|None=None):
        self.content, self.user, self.type, self.mention, self.chan = content,user,typ,mention,chan
class Message: # Message object
    def __init__(self, content:str, chan:str, nick:str):
        self.content = content
        self.channel = chan
        self.nick = nick
class ParserMessage: # Parser message
    def __init__(self, content, chan:str|None=None):
        self.content, self.chan = content, chan
class Channel: # Channel object
    is_init = False # If the channel's properties are initialized yet
    topic = "" # Channel topic
    modes = "+nt" # Channel modes
    in_channel = True # If the user is in the channel
    def __init__(self, name:str):
        self.name = name
    def info_set(self, topic:str, modes:str): # Socket will automatically initialize the channel object
        self.is_init = True
        self.topic, self.modes = topic, modes
class User: # User object
    def __init__(self, name:str, system:bool=False, realname:str|None=None, username:str|None=None, host:str|None=None):
        self.name, self.system, self.realname, self.username = name,system,realname,username
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
    def __init__(self, address:str="irc.libera.chat", port:int=6697, nick:str="CaneSugar", user:str="ScParse", ssl:bool=True, ssl_igninvalid:bool=False, realname:str="SugarcaneParseIRC user", **kwargs): # Contains the configuration
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.context = ssl_module.create_default_context()
        self.wsocket = None
        self.server, self.port, self.nick, self.user, self.ssl, self.ssl_accept_invalid, self.realname = address,port,nick,user,ssl,ssl_igninvalid,realname
        self.msgcache_index=0
        self.motd = ""
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
    def detach_connection(self):
        print("Detaching connection to a thread...")
        threading.Thread(target=self.getloop,daemon=True).start()
    def getloop(self):
        while self.connected:
            try:
                self.get()
            except:
                pass
    def send(self, content:str): # Attempt to send raw data to the socket
        if content[len(content)-1] != "\n":
            content+="\n"
        if self.ssl:
            self.wsocket.send(bytes(content,"UTF-8"))
        else:
            self.socket.send(bytes(content,"UTF-8"))
    def quit(self, message:str="ScParseIRC v"+str(__version__)): # Send the server a signal that the client is about to quit, and rely on the server to close the connection.
        self.send("QUIT :" + message + "\n")
        self.connected = False
    def join(self, chan):
        self.chans.append(Channel(chan))
        self.send(f"JOIN {chan}")
    def part(self, chan:str, message:str="ScParseIRC v"+str(__version__)):
        complete = False
        for i in self.chans:
            if i.name == chan:
                i.in_channel = False
                complete = True
                break
        if complete:
            self.send(f"PART {chan}")
    def privmsg(self, target:str, content:str):
        self.send(f"PRIVMSG {target} :{content}")
        self.messages.append(Message(content=content, chan=target, nick=self.nick))
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
        if r.find("PING") != -1:
            self.send(
               "PONG " + r.split()[1] + "\r\n"
            )
        if not r:
            self.connected = False
        return r
    def parseall(self): # Parse all of the fetched raw data, in a thread.
        threading.Thread(target=self._dump_message_cache, kwargs={"content": self.raw_text}).start()
    def _dump_message_cache(self, content:str): # The thread of parsing all of the raw data, dumping all of it in the messages list.
        self.messages = self.parse(content)
    def parse(self, content:str): # Attempt to parse raw data into a Message or SystemMessage object
        cache = []
        for i in content.replace("\r\n", "\n").split("\n"):
            spaced = i.split(" ")
            system_ = not "@" in spaced[0]
            if len(spaced) > 4:
                if spaced[1] == "NOTICE":
                    cache.append(SystemMessage(content=" ".join(spaced[3:])[1:],user=User(name=spaced[0][1:] if not "@" in spaced[0] else spaced[0][1:].split("!")[0], system=system_), typ="notice", mention=not system_))
                elif spaced[1] == "001":
                    cache.append(ParserMessage(content="Server reports name \"" + spaced[6] + "\""))
                elif spaced[1] == "003":
                    cache.append(ParserMessage(content="Server reports creation time " + " ".join(spaced[7:])))
                elif spaced[1] == "433":
                    cache.append(SystemMessage(content=" ".join(spaced[4:])[1:],user=User(name=spaced[0][1:], system=True), typ="error", mention=True))
        if len(cache) == 1:
            return cache[0]
        else:
            return cache
    def alive(self): # NOT FINISHED: To minimize exceptions, the client can ask the object if the socket connection is still alive.
        return False
    def whois(self, nick:str): # NOT FINISHED: Try to /whois the user, will return a user() object or None.
        return None