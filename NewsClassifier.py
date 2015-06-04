import os
import json
import re
import threading

class NewsClassifier:
	
	def __init__(self, TrainingSetpath, messageQueue):
		
		self.trainingSetpath = TrainingSetpath
		self.messageQueue = messageQueue
		self.__Train__(self.trainingSetpath)
		self.classifierThreads = []
	
	def Classify(self):
		return
	
	def GetClassifierThreads(self):
		return self.classifierThreads

	
	def __Train__(self, trainingSetpath):
		return
					
	def __TokenizeText__(self, text):
		return re.findall('[a-z]+', text.lower())
	
class NaiveBayesClassifier(NewsClassifier):
	
	def __init__(self, TrainingSetpath, crawlerQueue):
		NewsClassifier.__init__(self, TrainingSetpath, crawlerQueue)
				
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
			
	def __Train__(self, path):
		
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
						
	def __Classify__(self):
		
		while True:
			
			# blocking call
			self.messageQueue.crawlerQSema.acquire(True)
							
			self.messageQueue.crawlerQLock.acquire()
			
			# (text,headline,url)
			newsTuple = self.messageQueue.crawlerQ.popleft()
		
			self.messageQueue.crawlerQLock.release()
			
			words = self.__TokenizeText__(newsTuple[0])
			
			className = self.__ComputeClass__(words)
			
			self.__FillRankerQ__((className, newsTuple[1], newsTuple[2]))
	
	def __FillRankerQ__(self, rankerTuple):
	
		try:
			self.messageQueue.rankerQLock.acquire()
						
			self.messageQueue.rankerQ.append(rankerTuple)
					
			self.messageQueue.rankerQSema.release()
						
		finally:
			self.messageQueue.rankerQLock.release()
			
			
	def Classify(self):
				
		# only one classifying thread for now
		for i in range(1):
			self.classifierThreads.append(threading.Thread(target=self.__Classify__))
			self.classifierThreads[len(self.classifierThreads) - 1].start()
		
		

