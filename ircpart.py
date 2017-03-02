import threading
import socket
import commonUtils
import re

def setServer(server):
	self.server = server

def setChannel(channel):
	self.channel = channel

def setBotNick(botnick):
	self.botnick = botnick

class IRCThread(threading.Thread):
	def __init__(self, threadID, name, server, channel, botnick, queue):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.server = server
		self.channel = channel
		self.botnick = botnick
		self.pinged = False
		self.ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def run(self):
		commonUtils.log_info("Starting " + self.name)
		commonUtils.log_info("Connecting to " + self.server + " as " + self.botnick)
		self.ircsock.connect((self.server, 6667)) #here we connect to the server using port 6667
		self.ircsock.send("USER "+ self.botnick+ " "+self.botnick+" "+self.botnick+" :This bot is a result of a tutorial covered on http://shellium.org/wiki.\n") #user auth
		self.ircsock.send("NICK "+ self.botnick +"\n") #here we actually assign the nick to the bot

		#execution loop
		while 1:
			ircmsg = self.ircsock.recv(2048) #recieve data from server
			ircmsg = ircmsg.strip('\n\r') #removing unnecessary linebreaks
			if ircmsg.find("PING :") != -1: #if the server pings us then we've got to respond!
			    self.ping()
			    if not self.pinged:
			    	self.joinchan(self.channel)
			    self.pinged = True
			#this is sorta gross and will be refactored ~eventually~
			if self.pinged:
			    if ircmsg.lower().find(":is it") != -1:
			    	ircmsg = ircmsg.lower()
			    	isIt = re.search('is it (\w+) time yet?', ircmsg)
			    	if isIt:
			    		lunch = re.search('lunch', ircmsg)
			    		if lunch:
			    			self.sendmsg(self.channel, self.closeTo(1))
			    		else:
			    			quit = re.search('quitting', ircmsg)
			    			if quit:
			    				self.sendmsg(channel,self.closeTo(2))
			    if ircmsg.find(":Hello "+botnick) != -1:
			        self.hello()
			    if not self.tweetQueue.empty():
			    	self.shibe(self.tweetQueue.get())
    

	def ping(self): #responds to server pings
	    commonUtils.log_info(" Responding to ping")
	    self.ircsock.send("PONG :Pong\n")

	def sendmsg(self, chan , msg): #Send message function, sends msg to chan
	    commonUtils.log_info("Sending " + msg + " to " + chan)
	    self.ircsock.send("PRIVMSG "+ chan +" :"+ msg + "\n")

	def joinchan(self, chan): #function used to join channels
	    commonUtils.log_info("Joining " + chan)
	    self.ircsock.send("JOIN " + chan + "\n")

	def hello(self): #This function responds to a user that inputs "Hello Mybot"
	    commonUtils.log_info("Executing function Hello")
	    self.ircsock.send("PRIVMSG "+ channel +" :Hello!\n")

	def closeTo(self, time):
		now = datetime.datetime.now()
		if time == 1:
			prelunch = now.replace(hour=11, minute=0, second=0)
			lunch = now.replace(hour=12, minute=0, second=0)
			afterlunch = now.replace(hour=13, minute=0, second=0)
			if (prelunch) < now < (lunch):
				return "Almost!"
			elif (lunch) < now < (afterlunch):
				return "Hell yeah it is!"
			else:
				return "Nope"
		elif time == 2:
			hiltzquit = now.replace(hour=15, minute=30, second=0)
			quit = now.replace(hour=16, minute=0, second=0)
			mikequit = now.replace(hour=17, minute=0, second=0)
			waylate = now.replace(hour=20, minute=0, second=0)
			retString = "Nope"
			if hiltzquit < now:
				retString = "For NoNamesOverTheNet"
			if quit < now:
				retString += ", chickenwing, gh0st"
			if mikequit < now:
				retString += ", and thamunsta!"
			if waylate < now:
				retString = "JESUS YES GO HOME!"
			return retString
		else:
			return "idkmybffjill"


	def shibe(self, url):
		commonUtils.log_info("Posting a shibe")
		self.ircsock.send("PRIVMSG "+ channel + " :"+ url + "\n")