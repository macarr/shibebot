import threading
from Queue import Queue
import ConfigParser
import json
import socket
import requests
import datetime
import re
import logging

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API

#global vars
tweetQueue = Queue()
server = "irc.nervesocket.com" #server
channel = "#lobby" #Channel
botnick = "ShibeBot" #Bot nickname
username = "shibesbot" #twitter accountname
timestampPattern = '%Y-%m-%d %H:%M:%S' #for logging

#return an api object for twitter
def get_api(cfg):
	auth = OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
	auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
	return API(auth)

#take a tweet and return the media url from that tweet
def extract_url(tweet):
	try:
		mediaArray = tweet.get('entities',{}).get('media')
		if mediaArray[0]:
			url = mediaArray[0].get('media_url_https')
		else:
			url = ""
	except ReferenceError:
		url = ""
		log_error("Error extracting url, dumping tweet\n" + tweet)
	return url

#return the current datetime for logging
def timestamp():
	return str(datetime.datetime.now().strftime(timestampPattern))

def log_info(msg):
	print(msg + "\n")
	logging.info(msg)

def log_error(err):
	print(err + "\n")
	logging.warning(err)

class ProcessTweet(StreamListener):

	def on_data(self, data):
		tweet = json.loads(data.strip())

		screenName = tweet.get('user',{}).get('screen_name')
		log_info(str(timestamp()) + ": TWEET FROM: " + str(screenName) + " || LOOKING FOR: " + str(username))
		if screenName == username:
			log_info("found one!")
			url = extract_url(tweet)
			log_info(url)
			if not(url == ""):
				tweetQueue.put(url)
			else:
				log_error("Wrong media")
		log_info("done")

	def on_error(self, status):
		log_error(str(timestamp()) + ": " + status)

class TwitterThread(threading.Thread):
	def __init__(self, threadID, name):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name

	def run(self):
		log_info(str(timestamp()) + ": Starting "+ self.name)
		keyfile = open('twitter_keys.txt', 'r')
		cfg = json.loads(keyfile.read()) #todo: load from config file
		api = get_api(cfg)
		auth = OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
		auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
		streamListener = ProcessTweet()
		twitterStream = Stream(auth, streamListener)
		twitterStream.userstream()

class IRCThread(threading.Thread):
	def __init__(self, threadID, name):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.pinged = False
		self.ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def run(self):
		log_info(str(timestamp()) + ": Starting " + self.name)
		self.ircsock.connect((server, 6667)) #here we connect to the server using port 6667
		self.ircsock.send("USER "+botnick+ " "+botnick+" "+botnick+" :This bot is a result of a tutorial covered on http://shellium.org/wiki.\n") #user auth
		self.ircsock.send("NICK "+ botnick +"\n") #here we actually assign the nick to the bot

		#execution loop
		while 1:
			ircmsg = self.ircsock.recv(2048) #recieve data from server
			ircmsg = ircmsg.strip('\n\r') #removing unnecessary linebreaks
			if ircmsg.find("PING :") != -1: #if the server pings us then we've got to respond!
			    self.ping()
			    if not self.pinged:
			    	self.joinchan(channel)
			    self.pinged = True
			if self.pinged:
			    if ircmsg.lower().find(":is it") != -1:
			    	ircmsg = ircmsg.lower()
			    	isIt = re.search('is it (\w+) time yet?', ircmsg)
			    	if isIt:
			    		lunch = re.search('lunch', ircmsg)
			    		if lunch:
			    			self.sendmsg(channel, self.closeTo(1))
			    		else:
			    			quit = re.search('quitting', ircmsg)
			    			if quit:
			    				self.sendmsg(channel,self.closeTo(2))
			    if ircmsg.find(":Hello "+botnick) != -1:
			        self.hello()
			    if not tweetQueue.empty():
			    	self.shibe(tweetQueue.get())
    

	def ping(self): #responds to server pings
	    log_info(str(timestamp()) + ": Responding to ping")
	    self.ircsock.send("PONG :Pong\n")

	def sendmsg(self, chan , msg): #Send message function, sends msg to chan
	    log_info(str(timestamp()) + ": Sending " + msg + " to " + chan)
	    self.ircsock.send("PRIVMSG "+ chan +" :"+ msg + "\n")

	def joinchan(self, chan): #function used to join channels
	    log_info(str(timestamp()) + ": Joining " + chan)
	    self.ircsock.send("JOIN " + chan + "\n")

	def hello(self): #This function responds to a user that inputs "Hello Mybot"
	    log_info(str(timestamp()) + ": Executing function Hello")
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
		log_info(str(timestamp()) + ": Posting a shibe")
		self.ircsock.send("PRIVMSG "+ channel + " :"+ url + "\n")


def main():
	logging.basicConfig(filename = 'shibebot.log',level=logging.INFO)

	log_info("Bot startup!")

	twitterThread = TwitterThread(1, "Twitter")
	ircThread = IRCThread(2, "IRC")

	twitterThread.start()
	ircThread.start()

	log_info( str(timestamp()) + ": Exiting Main Thread")


if __name__ == "__main__":
	main()
	