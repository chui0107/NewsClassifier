from CrawlingAlgorithm import CrawlingOption

class TrainingCrawler:
	def __init__(self, newsHosts, categories, traningSetPath):
		self.newsHost = newsHosts
		self.categories = categories
		self.traningSetPath = traningSetPath
	
	def __SaveToFile__(self):
		return
		
	def Crawl(self):
		
		for host in self.newsHost:
			algo = host[1]
			algo.Crawl(CrawlingOption.TrainingCrawl, self.__SaveToFile__)
			
		return
		
	
