		
class NewsCrawler:
			
	def __init__(self, messageQueue):
		self.messageQueue = messageQueue
		self.crawlingAlgorithms = []
	
	def __Crawl__(self, algo):
		algo.Crawl(self.messageQueue)
	
	def AddAlgorithm(self, crawlingAlgorithm):
		self.crawlingAlgorithms.append(crawlingAlgorithm)
			
	def Crawl(self):
			
		import threading
		self.crawlingThreads = []
		
		for algo in self.crawlingAlgorithms:
			self.crawlingThreads.append(threading.Thread(target=self.__Crawl__, args=(algo,)))
			self.crawlingThreads[len(self.crawlingThreads) - 1].start()
		
	def GetCrawlerThreads(self):
		return self.crawlingThreads	
