
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
	
	import socket
	import sys
	
	# Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Connect the socket to the port where the server is listening
	server_address = ('localhost', 10000)
	print >> sys.stderr, 'connecting to %s port %s' % server_address
	sock.connect(server_address)

	try:	
		# Send data
		message = 'business'
		sock.sendall(message)	

	finally:
		print >> sys.stderr, 'closing socket'
		sock.close()
	
	return
					
if __name__ == "__main__":
	main()		
