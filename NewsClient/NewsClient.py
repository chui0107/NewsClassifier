
def SendRequest(message):
	
	import socket
	import json

		# Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Connect the socket to the port where the server is listening
	server_address = ('localhost', 10000)
	
	sock.connect(server_address)

	bufSize = 2018
	try:
		print message
		sock.sendall(message)
		jsonString = sock.recv(bufSize)
		
		if len(jsonString) == 0:
			raise RuntimeError("socket connection broken")
		
		replyJosn = json.loads(jsonString)
		if(replyJosn['status'] == 0):
			print 'Can\'t retrieve news for the category'
		else:
			print replyJosn['news']
	

	finally:
		sock.close()



def GetCommondLineInput():
	
	import shlex

	print 'Enter a subject of news to browse'
	print 'To get help, enter `help`.'
		
	while True:
		
		inputs = shlex.split(raw_input('Subject: '))
		if len(inputs) != 1:
			print 'Only support 1 input at this time'
			continue
			
		cmd = inputs[0].lower()
		
		if cmd == 'exit':
			break
		elif cmd == 'help':
			print 'To be added'	
		else:
			SendRequest(cmd)

def main():
	
	GetCommondLineInput()
	
					
if __name__ == "__main__":
	main()		
