import socket
import time

def main():

	host = '127.0.0.1'
	port = 11861

	server_ip_address = (host, port)

	# Create socket
	with socket.socket() as s:
		# Connect to a server
		s.connect(server_ip_address)

		while True:
			msg = "herro"
			s.sendall(msg.encode('utf-8'))
			data = s.recv(1024).decode('utf-8')
			print("Received: ", data)









if __name__ == '__main__':
	main()





