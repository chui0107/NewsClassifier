from CrawlingAlgorithm import CrawlingOption
import logging

class TrainingCrawler:
	def __init__(self, newsHosts, categories, traningSetPath):
		import collections
		
		self.newsHost = newsHosts
		self.categories = categories
		self.traningSetPath = traningSetPath
		self.categoriesDict = collections.defaultdict(lambda: [])
	
	def __SaveToFile__(self, newsTuple):
		category = newsTuple[0]
		title = newsTuple[2]
		text = newsTuple[1]
		self.categoriesDict[category].append((title, text))
				
	def __Flush__(self):
		
		for category in self.categoriesDict:
			logging.info('flushing %s news to the disk', category)
			print category
			text = str(self.categoriesDict[category])
			
			fileName = self.traningSetPath + category + '1.txt'
			
			with open(fileName, 'w+') as f:	
				f.write(text)
					
		self.categoriesDict.clear()
			
		
	def Crawl(self):
		
		for host in self.newsHost:
			algo = host[1]
			algo.Crawl(CrawlingOption.TrainingCrawl, self.__SaveToFile__, self.categories)
			
			break
		
		self.__Flush__()
		
		
	
