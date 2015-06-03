import os
import json
import re

class NewsClassifier:
	
	def __init__(self, TrainingSetpath, crawlerQueue):
		
		self.trainingSetpath = TrainingSetpath
		self.crawlerQueue = crawlerQueue
		self.__Train__(self.trainingSetpath)
	
	def __Train__(self, trainingSetpath):
		return
				
	def Classify(self):
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
						
	def __Classify__(self, newsTuple):
		words = self.__TokenizeText__(newsTuple[0])
		className = self.__ComputeClass__(words)
		return (className, newsTuple[1], newsTuple[2])
	
	def Classify(self):
		
		while True:
		
			self.crawlerQueue.messageQSema.acquire()
							
			self.crawlerQueue.messageQLock.acquire()
		
			newsTuple = self.crawlerQueue.messageQ.popleft()
		
			self.crawlerQueue.messageQLock.release()
		
			print self.__Classify__(newsTuple)[0]
		

