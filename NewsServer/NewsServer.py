import os
from NewsCrawler import NewsCrawler
from NewsCrawler import NewsHost
from NewsCrawler import MessageQueue
from NewsRanker import NewsRanker
from NewsClassifier import NaiveBayesClassifier
	 				
def main():
				
	curPath = os.getcwd()
	
	trainingSetPath = curPath + '/TrainingSet/'
	
	testSetPath = curPath + '/TestSet/'
	
	messageQueue = MessageQueue()

	newsClassifier = NaiveBayesClassifier(trainingSetPath, messageQueue)
	
	newsCrawler = NewsCrawler(messageQueue)
	
	nyTimes = NewsHost('http://api.nytimes.com/svc/search/v2/articlesearch', 'f01308a5d8db23dd5722469be240a909:14:67324777', 'http://developer.nytimes.com/docs/read/article_search_api_v2')
	
	newsCrawler.AddHost(nyTimes)
	
	# GetCommondLineInput()
	
	newsRanker = NewsRanker(messageQueue)

	newsCrawler.Crawl()
	
	newsClassifier.Classify()
	
	newsRanker.Rank()
	
	allThreads = []
	
	allThreads.append(newsCrawler.GetCrawlerThreads())
	
	allThreads.append(newsClassifier.GetClassifierThreads())
	
	allThreads.append(newsRanker.GetRankerThreads())
	
	for threads in allThreads:
		for thread in threads:
			thread.join()
					
	
if __name__ == "__main__":
	main()		