import datetime
import logging

timestampPattern = '%Y-%m-%d %H:%M:%S'

#return the current datetime for logging
def timestamp():
	return str(datetime.datetime.now().strftime(timestampPattern))

def log_info(msg):
	print(timestamp() + " : INFO : " + str(msg) + "\n")
	logging.info(timestamp() + " : " + str(msg) + "\n")

def log_error(err):
	print(timestamp() + " : ERROR : " + str(err) + "\n")
	logging.warning(timestamp() + " : " + str(err) + "\n")

def init():
	logging.basicConfig(filename = 'shibebot.log',level=logging.INFO)