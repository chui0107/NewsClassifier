
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
	return
					
if __name__ == "__main__":
	main()		
