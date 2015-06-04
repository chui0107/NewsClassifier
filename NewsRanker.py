class NewsRanker:
	
	def __init__(self, messageQueue):
		self.newsDict = {}
		self.messageQueue = messageQueue
		self.rankedNews = {}
		
	def Rank(self):
		return
	
	def RetrieveNews(self, className):
		if not className in self.rankedNews:
			print 'Currently don\'t support this categoriy'
			return
		
		return self.rankedNews[className]	
