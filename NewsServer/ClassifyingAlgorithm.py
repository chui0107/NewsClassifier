import abc
from cgitb import text

class ClassifyingAlgorithm:
	def __init__(self, messageQueue):
		self.messageQueue = messageQueue
	
	def __TokenizeText__(self, text):
		import re
		return re.findall('[a-z]+', text.lower())
	
	@abc.abstractmethod	
	def Train(self, trainingSetPath):
		return
	
	@abc.abstractmethod
	def Classify(self):
		return
	
	@abc.abstractmethod	
	def TestClassifier(self, testingSetPath):
		return

class NaiveBayes(ClassifyingAlgorithm):
	
	def __init__(self, messageQueue):
		ClassifyingAlgorithm.__init__(self, messageQueue)
				
	def __PopulateClass__(self, className, words):
		
		import collections
		
		classes = self.vocabulary[0]
		
		classes[className] = collections.defaultdict(lambda: 1)
		
		for word in words:
			classes[className][word] += 1
							
	def __ComputeClass__(self, words):
		
		import math
		
		classes = self.vocabulary[0]
		classPriores = self.vocabulary[1]
		vocabularySize = self.vocabulary[2]
		
		classMaxProb = -float("inf");
		className = ''
		
		for classKey in classes:
			
			classDict = classes[classKey]
			classWordSize = len(classDict)
			
			classPrior = classPriores[classKey]
			
			denominator = classWordSize + vocabularySize
			classProb = 0.0
			
			# bag of words model
			for word in words:
				
				# add one smoothing
				wordProb = 1.0 / denominator
				
				if word in classDict:	
					wordProb = wordProb + float(classDict[word]) / denominator
				
				# use log arithmetic to avoid multiplication overflow
				classProb = classProb + math.log(wordProb)
					
			classProb = classProb * classPrior
			# choose the class with max probability
			if classProb > classMaxProb:
				classMaxProb = classProb
				className = classKey
		
		return className
			
	def __ExtractCrawlerQ__(self):
			# blocking call
			self.messageQueue.crawlerQSema.acquire(True)
							
			self.messageQueue.crawlerQLock.acquire()
			
			# (text,headline,url)
			newsTuple = self.messageQueue.crawlerQ.popleft()
			
			self.messageQueue.crawlerQLock.release()
			
			words = self.__TokenizeText__(newsTuple[0])
			
			className = self.__ComputeClass__(words)
			
			return (className, newsTuple[1], newsTuple[2])
	
	def __FillRankerQ__(self, rankerTuple):
	
		try:
			self.messageQueue.rankerQLock.acquire()
			
			self.messageQueue.rankerQ.append(rankerTuple)
					
			self.messageQueue.rankerQSema.release()
						
		finally:
			self.messageQueue.rankerQLock.release()
			
	def Train(self, trainingSetPath):
		
		import os
		import ast
		
		self.vocabulary = []
		self.vocabulary.append({})
		
		for eachClass in os.listdir(trainingSetPath):
			
			fileName = eachClass.lower()
			
			if fileName.endswith("seeds.txt") or not fileName.endswith(".txt"):
				continue
			
			category = fileName[:-4]
			
			with open(trainingSetPath + eachClass, 'r') as f:
					
				text = f.read()
								
				words = self.__TokenizeText__(text)
						
				self.__PopulateClass__(category, words)
					
		# populate prior probabilities
		self.vocabulary.append({})
		
		classes = self.vocabulary[0]
		classesPrior = self.vocabulary[1]
		
		totolWords = 0
		
		for eachClass in classes:
			
			eachClassPriorProbability = 1.0 / len(classes)
			
			classesPrior[eachClass] = eachClassPriorProbability
			
			# populate total words
			wordInEachClass = len(classes[eachClass])
			totolWords += wordInEachClass
			
		self.vocabulary.append(totolWords)
							
	def TestClassifier(self, testingSetPath):
		
		import os
		import ast
		
		for eachClass in os.listdir(testingSetPath):
			
			fileName = eachClass.lower()
				
			if not fileName.endswith(".txt"):
				continue
			
			category = fileName[:-4]
			
			with open(testingSetPath + eachClass, 'r') as f:
				
				text = f.read()	
				newsTuples = ast.literal_eval(text)
				
				totalNews = 0
				mistake = 0
				
				for eachNews in newsTuples:
										
					text = eachNews[0] + ' ' + eachNews[1]
					
					words = self.__TokenizeText__(text)
					
					computedClassName = self.__ComputeClass__(words)
					
					totalNews += 1
					
					if computedClassName != category:
						mistake += 1
						
			print 'In %s category, the classifier achieved %0.2f accuracy (%d,%d)\n' % (category, (totalNews - mistake) / float(totalNews), (totalNews - mistake), totalNews)	
	
	def Classify(self):
		
		while True:
			rankerTuple = self.__ExtractCrawlerQ__()
			self.__FillRankerQ__(rankerTuple)
			
	
	
