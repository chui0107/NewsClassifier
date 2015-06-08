import abc

class ClassifyingAlgorithm:
	def __init__(self, messageQueue):
		self.messageQueue = messageQueue
	
	def __TokenizeText__(self, text):
		import re
		return re.findall('[a-z]+', text.lower())
	
	@abc.abstractmethod	
	def Train(self):
		return
	
	@abc.abstractmethod
	def Classify(self):
		return

class NaiveBayes(ClassifyingAlgorithm):
	
	def __init__(self, messageQueue):
		ClassifyingAlgorithm.__init__(self, messageQueue)
				
	def __PopulateClass__(self, className, words):
		
		classes = self.vocabulary[0]
		
		classes[className] = []
		
		wordCount = {}
		wordSize = 0
		
		for word in words:
			if word in wordCount:
				wordCount[word] = wordCount[word] + 1
			else:
				wordCount[word] = 1
				wordSize = wordSize + 1
						
		classes[className].append(wordCount)
		classes[className].append(wordSize)
	
	def __ComputeClass__(self, words):
		
		import math
		
		classes = self.vocabulary[0]
		vocabularySize = self.vocabulary[1]
		
		classMaxProb = -float("inf");
		className = ''
		
		for classKey in classes:
			
			classTuple = classes[classKey]
			classDict = classTuple[0]
			classWordSize = classTuple[1]
			classPrior = classTuple[2]
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
			
	def Train(self, path):
		
		import os
		import json
		
		self.vocabulary = []
		self.vocabulary.append({})
		
		for eachClass in os.listdir(path):
			
			fileName = eachClass.lower()
				
			# class file 
			extension = fileName[len(fileName) - 4:]
			if extension != '.txt':
				continue
				
			className = fileName[:len(fileName) - 4]
				
			with open(path + eachClass, 'r') as f:
					
				news = json.load(f)
				
				text = ''
		
				for eachnews in news:
			
					title = eachnews[1]
		
					description = eachnews[2]
		
				text += title + description	
				
				words = self.__TokenizeText__(text)
				
				self.__PopulateClass__(className, words)
					
		# populate prior probabilities
		classes = self.vocabulary[0]
		totolWords = 0
		
		for eachClass in classes:
			
			eachClassPriorProbability = 1.0 / len(classes)
			
			classes[eachClass].append(eachClassPriorProbability)
			
			# populate total words
			wordInEachClass = classes[eachClass][1]
			totolWords = totolWords + wordInEachClass
			
		self.vocabulary.append(totolWords)
							
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
			
			
	def Classify(self):
		
		while True:
			rankerTuple = self.__ExtractCrawlerQ__()
			self.__FillRankerQ__(rankerTuple)
	
