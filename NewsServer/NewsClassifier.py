
class NewsClassifier:
	
	def __init__(self, classifyAlgorithm, trainingSetPath, testingSetPath):
		
		self.classifyAlgorithm = classifyAlgorithm
		self.trainingSetPath = trainingSetPath
		self.testingSetPath = testingSetPath
		
		self.classifierThreads = []
		
	def Train(self):
		self.classifyAlgorithm.Train(self.trainingSetPath)
						
	def TestClassifier(self):
		self.classifyAlgorithm.TestClassifier(self.testingSetPath)
									
	def Classify(self):
		import threading
		
		# only one classifying thread for now
		for i in range(1):
			self.classifierThreads.append(threading.Thread(target=self.classifyAlgorithm.Classify))
			self.classifierThreads[len(self.classifierThreads) - 1].start()
		
	def GetClassifierThreads(self):
		return self.classifierThreads
