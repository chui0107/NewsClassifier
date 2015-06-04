import threading

class NewsRanker:
	
	def __init__(self, messageQueue):
		self.newsDict = {}
		self.messageQueue = messageQueue
		self.rankedNews = {}
		self.rankedNewsUrl = set()
		self.rankedNewsLock = threading.Lock()
		
	def __Rank__(self):
		
		while True:	
			
			newsTuple = self.__ExtractRankerQ__()
			
			if newsTuple:
				self.__FillRankedNewsDict__(newsTuple)
				
	def __FillRankedNewsDict__(self, newsTuple):
		className = newsTuple[0]
		headline = newsTuple[1]
		url = newsTuple[2]
		try:					
			self.rankedNewsLock.acquire()
			
			if not url in self.rankedNewsUrl:
				self.rankedNewsUrl.add(url)
				
				if not className in self.rankedNews:
					self.rankedNews[className] = []
					
				self.rankedNews[className].append((headline, url))
			
		finally:
			self.rankedNewsLock.release()
			
	def __ExtractRankerQ__(self):
		
		newsTuple = None			
		try:
			# blocking call
			self.messageQueue.rankerQSema.acquire(True)
							
			self.messageQueue.rankerQLock.acquire()
			
			newsTuple = self.messageQueue.rankerQ.popleft()
		
		finally:
			self.messageQueue.rankerQLock.release()
			
		return newsTuple	
				
	def Rank(self):
		
		self.rankerThreads = []
		# one ranker thread for now
		for i in range(1):
			self.rankerThreads.append(threading.Thread(target=self.__Rank__))
			self.rankerThreads[len(self.rankerThreads) - 1].start()
	
	def GetRankerThreads(self):
		return self.rankerThreads
	
	def RetrieveNews(self, className):
		
		news = []
		try:					
			self.rankedNewsLock.acquire()
			
			if className in self.rankedNews:
				news = self.rankedNews[className]
			else:
				print 'Currently don\'t support this category' 
				
		finally:
			self.rankedNewsLock.release()
			return news
		