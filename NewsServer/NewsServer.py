import os
import sys
import logging
from NewsBase import NewsHost
from NewsBase import MessageQueue
from NewsCrawler import NewsCrawler
from RankingAlgorithm import RankingAlgorithm
from CrawlingAlgorithm import NYtimesCrawlingAlgorithm
from CrawlingAlgorithm import USATodayCrawlingAlgorithm
from ClassifyingAlgorithm import NaiveBayes
from NewsRanker import NewsRanker
from NewsClassifier import NewsClassifier
from TrainingCrawler import TrainingCrawler

class NewsServer:
	def __init__(self, host, port, newsRanker):
		import socket

		self.host = host
		self.port = port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = (self.host, self.port)
		self.sock.bind(server_address)
		self.sock.listen(1)
		print 'Starting up server on %s port %s' % server_address
		
		self.newsRanker = newsRanker
	
	def __Start__(self):
		
		import json
		bufSize = 2048
		
		while True:
			
			connection, client_address = self.sock.accept()
			print 'connection from', client_address
			
			try:
				
				data = connection.recv(bufSize)
				if data == '':
					print "Connection issue:", sys.exc_info()[0]
					continue
			
				data = data.lower()
				replyJson = {'status':0, 'news':None}
				news = self.newsRanker.RetrieveNews(data)
					
				if news:
					replyJson['status'] = 1
					replyJson['news'] = json.dumps(news)
					
				connection.sendall(json.dumps(replyJson))
				
			except:
				print "Unexpected error:", sys.exc_info()[0]
			
			finally:
				connection.close()
		
	
	def Start(self):
		
		import threading
		
		self.serverThreads = []
		# only one server thread for now
		for i in range(1):
			self.serverThreads.append(threading.Thread(target=self.__Start__))
			self.serverThreads[len(self.serverThreads) - 1].start()
		
			
	def GetServerThreads(self):
		return self.serverThreads
	

def main():
	
	logging.basicConfig(filename='SystemLog.log', filemode='w', format='%(asctime)s | %(levelname)s: | %(message)s', level=logging.INFO)
	
	logging.info('Starting up the system')
	
	enableTrainingSetCrawler = False
	enableTestSet = True
				
	curPath = os.getcwd()
	
	trainingSetPath = curPath + '/TrainingSet/'
	
	testingSetPath = curPath + '/TestSet/'
	
	messageQueue = MessageQueue()
	
	newsHosts = []
	nyTimesHost = NewsHost('http://api.nytimes.com/svc/search/v2/articlesearch', 'f01308a5d8db23dd5722469be240a909:14:67324777', 'http://developer.nytimes.com/docs/read/article_search_api_v2')
	nyTimesHostAlgo = NYtimesCrawlingAlgorithm(nyTimesHost)
	newsHosts.append((nyTimesHost, nyTimesHostAlgo)) 
	
	usaTodayHost = NewsHost('http://api.usatoday.com/open/articles', 'b5vr5crn4xryqh2p4ppbybjv', 'http://developer.usatoday.com/docs/read/articles')
	usaTodayHostAlgo = USATodayCrawlingAlgorithm(usaTodayHost)
	newsHosts.append((usaTodayHost, usaTodayHostAlgo))
	
	newsCategories = []
	newsCategories.append('business')
	
	if enableTrainingSetCrawler:
		logging.info('Running traningSetCrawler')
		trainingCrawler = TrainingCrawler(newsHosts, newsCategories, trainingSetPath)
		trainingCrawler.Crawl()
		return
	
	naiveBayes = NaiveBayes(messageQueue)
	newsClassifier = NewsClassifier(naiveBayes, trainingSetPath, testingSetPath)
	newsClassifier.Train()
	
	if enableTestSet:
		logging.info('Testing classifier from local files')
		newsClassifier.TestClassifier()
		return
	
	newsCrawler = NewsCrawler(messageQueue)
	
	for newsHost in newsHosts:
		newsCrawler.AddAlgorithm(newsHost[1])
	
	rankingAlgorithm = RankingAlgorithm()
	
	newsRanker = NewsRanker(messageQueue, rankingAlgorithm)

	newsCrawler.Crawl()
	
	newsClassifier.Classify()
	
	newsRanker.Rank()
	
	newsServer = NewsServer('localhost', 10000, newsRanker)
	newsServer.Start()
	
	logging.info('All threads started, waiting for inquires')
	
	allThreads = []
	
	allThreads.append(newsServer.GetServerThreads())
	
	allThreads.append(newsCrawler.GetCrawlerThreads())
	
	allThreads.append(newsClassifier.GetClassifierThreads())
	
	allThreads.append(newsRanker.GetRankerThreads())
	
	for threads in allThreads:
		for thread in threads:
			thread.join()
					
	
if __name__ == "__main__":
	main()		
