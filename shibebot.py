import twitterpart
import commonUtils
import ircpart

from Queue import Queue

def main():
	#init logging
	commonUtils.init()
	commonUtils.log_info("Bot Startup!")

	#config vars
	ircServ = "irc.nervesocket.com"
	channel = "#lobby"
	botNick = "shibebot"

	tweetQueue = Queue()

	twitterThread = twitterpart.TwitterThread(1, "Twitter", tweetQueue)
	ircThread = ircpart.IRCThread(2, "IRC", ircServ, channel, botNick, tweetQueue)


	twitterThread.start()
	ircThread.start()

	commonUtils.log_info("Exiting main thread")



if __name__ == "__main__":
	main()