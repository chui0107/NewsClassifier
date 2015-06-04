class NewsRanker:
	
	def __init__(self, crawlerQueue):
		self.newsDict = {}
		self.crawlerQueue = crawlerQueue
		self.rankedNews = {}
		
	def Rank(self):
		return
	
	def RetrieveNews(self, className):
		if not className in self.rankedNews:
			print 'Currently don\'t support this categoriy'
			return
		
		return self.rankedNews[className]	
