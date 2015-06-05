import os
import sys
from NewsCrawler import NewsCrawler
from NewsCrawler import NewsHost
from NewsCrawler import MessageQueue
from NewsRanker import NewsRanker
from NewsClassifier import NaiveBayesClassifier
from RankingAlgorithm import RankingAlgorithm

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
		
		bufSize = 100
		
		while True:
			
			connection, client_address = self.sock.accept()
			
			try:
				print sys.stderr, 'connection from', client_address

				# Receive the data in small chunks and retransmit it
				while True:
					
					data = connection.recv(bufSize).lower()
					
					if data:
						if data == 'business':
							news = self.newsRanker.RetrieveNews(data)
							if news:
								print '1'
					else:
						break
			
			finally:
				# Clean up the connection
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
				
	curPath = os.getcwd()
	
	trainingSetPath = curPath + '/TrainingSet/'
	
	testSetPath = curPath + '/TestSet/'
	
	messageQueue = MessageQueue()

	newsClassifier = NaiveBayesClassifier(trainingSetPath, messageQueue)
	
	newsCrawler = NewsCrawler(messageQueue)
	
	nyTimes = NewsHost('http://api.nytimes.com/svc/search/v2/articlesearch', 'f01308a5d8db23dd5722469be240a909:14:67324777', 'http://developer.nytimes.com/docs/read/article_search_api_v2')
	
	newsCrawler.AddHost(nyTimes)
	
	rankingAlgorithm = RankingAlgorithm()
	newsRanker = NewsRanker(messageQueue, rankingAlgorithm)

	newsCrawler.Crawl()
	
	newsClassifier.Classify()
	
	newsRanker.Rank()
	
	newsServer = NewsServer('localhost', 10000, newsRanker)
	newsServer.Start()
	
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
