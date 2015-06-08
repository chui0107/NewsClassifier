
class MessageQueue:
	def __init__(self):
		import collections
		import threading
		# NOTE that collections.deque() is thread-safe
		# https://docs.python.org/2/library/collections.html#collections.deque
		self.crawlerQ = collections.deque()
		# set the initial value of the semaphore to be 0
		self.crawlerQSema = threading.Semaphore(0)
		self.crawlerQLock = threading.Lock()
		
		self.rankerQ = collections.deque()
		# set the initial value of the semaphore to be 0
		self.rankerQSema = threading.Semaphore(0)
		self.rankerQLock = threading.Lock()
					
class NewsHost:
	def __init__(self, url, apiKey, docLink):
		self.url = url
		self.apiKey = apiKey
		self.docLink = docLink