import threading
		
class MessageQueue:
	def __init__(self):
		import collections
		# NOTE that collections.deque() is thread-safe
		# https://docs.python.org/2/library/collections.html#collections.deque
		self.crawlerQ = collections.deque()
		# set the initial value of the semaphore to be 0
		self.crawlerQSema = threading.Semaphore(0)
		self.crawlerQLock = threading.Lock()
		
		self.rankerQ = collections.deque()
		# set the initial value of the semaphore to be 0
		self.rankerQSema = threading.Semaphore(0)
		self.rankerQLock = threading.Lock()
					
class NewsCrawler:
			
	def __init__(self, messageQueue):
		self.messageQueue = messageQueue
		self.crawlingAlgorithms = []
	
	def __Crawl__(self, algo):
		algo.Crawl(self.messageQueue)
	
	def AddAlgorithm(self, crawlingAlgorithm):
		self.crawlingAlgorithms.append(crawlingAlgorithm)
			
	def Crawl(self):
			
		self.crawlingThreads = []
		
		for algo in self.crawlingAlgorithms:
			self.crawlingThreads.append(threading.Thread(target=self.__Crawl__, args=(algo,)))
			self.crawlingThreads[len(self.crawlingThreads) - 1].start()
		
	def GetCrawlerThreads(self):
		return self.crawlingThreads	
