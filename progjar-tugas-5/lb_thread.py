import socket
import time
import sys
import threading
import logging


class BackendList:
	def __init__(self):
		self.servers=[]
		self.servers.append(('127.0.0.1',8001))
		self.servers.append(('127.0.0.1',8002))
		self.servers.append(('127.0.0.1',8003))
		self.current=0
	def getserver(self):
		s = self.servers[self.current]
		self.current=self.current+1
		if (self.current>=len(self.servers)):
			self.current=0
		return s


class Backend(threading.Thread):
	def __init__(self,targetaddress):
		self.target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.targetaddress = targetaddress
		threading.Thread.__init__(self)

	def run(self):
		data = self.target_sock.recv(32)
		print("Server say {}".format(data.decode()))
		self.client_socket.send(data)
		# self.close()
		# self.client_socket.close()

class ProcessTheClient(threading.Thread):
	def __init__(self,connection):
		self.client_connection = connection
		threading.Thread.__init__(self)

	def run(self):
		data = self.client_connection.recv(32)
		print("Client say {}".format(data.decode()))
		
		if data:
			self.backend.client_socket = self.client_connection
			self.backend.target_sock.connect(self.backend.targetaddress)
			self.backend.target_sock.send(data)
			self.backend.start()

class Server(threading.Thread):
	def __init__(self,portnumber):
		self.the_clients = []
		self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.portnumber = portnumber
		self.bservers = BackendList()
		threading.Thread.__init__(self)
		logging.warning("load balancer running on port {}" . format(portnumber))

	def run(self):
		self.server_sock.bind(('0.0.0.0', self.portnumber))
		self.server_sock.listen(1)
		while True:
			self.connection, self.client_address = self.server_sock.accept()
			logging.warning("connection from {}".format(self.client_address))

			#menentukan ke server mana request akan diteruskan
			bs = self.bservers.getserver()
			logging.warning("koneksi dari {} diteruskan ke {}" . format(self.client_address, bs))
			backend = Backend(bs)

			#mendapatkan handler dan socket dari client
			handler = ProcessTheClient(self.connection)
			handler.backend = backend
			handler.start()
			self.the_clients.append(handler)
		

def main():
	portnumber=55555
	try:
		portnumber=int(sys.argv[1])
	except:
		pass
	svr = Server(portnumber)
	svr.start()

if __name__=="__main__":
	main()


