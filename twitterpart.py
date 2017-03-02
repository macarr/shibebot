from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API

import commonUtils
import json
import ConfigParser
import threading

#return an api object for twitter
def get_api(cfg):
	auth = OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
	auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
	return API(auth)

#take a tweet and return the media url from that tweet
#TODO: stop this from crashing the bot
def extract_url(tweet):
	try:
		mediaArray = tweet.get('entities',{}).get('media')
		if mediaArray[0]:
			url = mediaArray[0].get('media_url_https')
		else:
			url = ""
	except ReferenceError:
		url = ""
		commonUtils.log_error("Error extracting url, dumping tweet\n" + tweet)
	return url

class ProcessTweet(StreamListener):

	def on_data(self, data):
		tweet = json.loads(data.strip())

		screenName = tweet.get('user',{}).get('screen_name')
		commonUtils.log_info("TWEET FROM: " + str(screenName) + " || LOOKING FOR: " + str(self.username))
		if screenName == self.username:
			commonUtils.log_info("found one!")
			url = extract_url(tweet)
			commonUtils.log_info(url)
			if not(url == ""):
				self.tweetQueue.put(url)
			else:
				commonUtils.log_error("Wrong media")
		commonUtils.log_info("done")

	def on_error(self, status):
		commonUtils.log_error(str(status))

class TwitterThread(threading.Thread):
	def __init__(self, threadID, name, tweetQueue, username):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.tweetQueue = tweetQueue
		self.username = username

	def run(self):
		commonUtils.log_info(" Starting "+ self.name)
		keyfile = open('twitter_keys.txt', 'r')
		cfg = json.loads(keyfile.read()) #todo: load from config file
		api = get_api(cfg)
		auth = OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
		auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
		streamListener = ProcessTweet()
		twitterStream = Stream(auth, streamListener)
		twitterStream.userstream()