from CrawlingAlgorithm import CrawlingOption

# this class generate seed urls for the NewsScraper		
class NewsCrawler:
			
	def __init__(self, messageQueue):
		self.messageQueue = messageQueue
		self.crawlingAlgorithms = []
	
	def __FillCrawlerQ__(self, newsTuple):
		try:
			self.messageQueue.crawlerQLock.acquire()
					
			self.messageQueue.crawlerQ.append(newsTuple)
					
			self.messageQueue.crawlerQSema.release()
						
		finally:
			self.messageQueue.crawlerQLock.release()	
	
	def AddAlgorithm(self, crawlingAlgorithm):
		self.crawlingAlgorithms.append(crawlingAlgorithm)
			
	def Crawl(self):
			
		import threading
		self.crawlingThreads = []
		
		for algo in self.crawlingAlgorithms:
			self.crawlingThreads.append(threading.Thread(target=algo.Crawl, args=(CrawlingOption.RunningCrawl, self.__FillCrawlerQ__, None)))
			self.crawlingThreads[len(self.crawlingThreads) - 1].start()
		
	def GetCrawlerThreads(self):
		return self.crawlingThreads
	