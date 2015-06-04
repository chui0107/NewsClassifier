import os
from NewsCrawler import NewsCrawler
from NewsCrawler import NewsHost
from NewsCrawler import MessageQueue
from NewsRanker import NewsRanker
from NewsClassifier import NaiveBayesClassifier

def GetCommondLineInput():
	
	import readline
	import shlex
	
	print 'Enter a subject of news to browse'
	print 'To get help, enter `help`.'
	
	subjects = frozenset(['business', 'politics', 'entertainment'])
	
	while True:
		
		inputs = shlex.split(raw_input('Subject: '))
		if len(inputs) != 1:
			print 'Only support 1 input at this time'
			continue
			
		cmd = inputs[0].lower()
		
		if cmd in subjects:
			print 'in'
			continue;
						
		if cmd == 'exit':
			break

		elif cmd == 'help':
			print 'To be added'
	
		else:
			print('Unknown command: {}'.format(cmd))		 
				
def main():
				
	curPath = os.getcwd()
	
	trainingSetPath = curPath + '/TrainingSet/'
	
	testSetPath = curPath + '/TestSet/'
	
	messageQueue = MessageQueue()

	classifier = NaiveBayesClassifier(trainingSetPath, messageQueue)
	
	newsCrawler = NewsCrawler(messageQueue)
	
	nyTimes = NewsHost('http://api.nytimes.com/svc/search/v2/articlesearch', 'f01308a5d8db23dd5722469be240a909:14:67324777', 'http://developer.nytimes.com/docs/read/article_search_api_v2')
	
	newsCrawler.AddHost(nyTimes)
	
	# GetCommondLineInput()
	
	newsRanker = NewsRanker(messageQueue)

	newsCrawler.Crawl()
	
	classifier.Classify()
	
	allThreads = []
	
	allThreads.append(newsCrawler.GetCrawlerThreads())
	
	allThreads.append(classifier.GetClassifierThreads())
	
	for threads in allThreads:
		for thread in threads:
			thread.join()
					
	
	
if __name__ == "__main__":
	main()		