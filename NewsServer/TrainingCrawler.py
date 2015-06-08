from CrawlingAlgorithm import CrawlingOption
import logging

class TrainingCrawler:
	def __init__(self, newsHosts, categories, traningSetPath):
		import collections
		
		self.newsHost = newsHosts
		self.categories = categories
		self.traningSetPath = traningSetPath
		
		self.categoriesDictCounter = 0
		self.categoriesDictFlushSize = 50
		self.categoriesDict = collections.defaultdict(lambda: [])
	
	def __SaveToFile__(self, newsTuple):
		category = newsTuple[0]
		title = newsTuple[2]
		text = newsTuple[1]
		self.categoriesDict[category].append((title, text))
		
		self.categoriesDictCounter += 1
		
		# flush every every 100
		if(self.categoriesDictCounter >= self.categoriesDictFlushSize):
			self.__Flush__()
				
	def __Flush__(self):
		
		logging.info('flushing to the disk')
		for category in self.categoriesDict:
				
			text = ''
			for eachTuple in self.categoriesDict[category]:
				text += str(eachTuple)
			
			fileName = self.traningSetPath + category + '1.txt'
			with open(fileName, 'a+') as f:			
				f.write(text)
					
		self.categoriesDictCounter = 0	
		self.categoriesDict.clear()
			
		
	def Crawl(self):
		
		for host in self.newsHost:
			algo = host[1]
			algo.Crawl(CrawlingOption.TrainingCrawl, self.__SaveToFile__, self.categories)
			
			break
		
		self.__Flush__()
		
		
	
