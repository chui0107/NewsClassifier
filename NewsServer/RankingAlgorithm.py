import abc

class RankingAlgorithm:
	def __init__(self):
		return
	
	@abc.abstractmethod
	def Rank(self, news=[], features=[]):
		return
	
