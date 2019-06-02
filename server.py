import sys	# CLI arguments
import socket
import json
import time
import aiohttp  # Asynchronous IO with HTTP

class IAMAT:
	# Parse IAMAT formatted data
	def __init__(self, data):
		# IAMAT <client id>	<gps coordinates> <time client sent message>
		# IAMAT kiwi.cs.ucla.edu +34.068930-118.445127 1520023934.918963997
		split_data = data.split(" ")
		self.client_id = split_data[1]
		self.gps = split_data[2]
		self.timestamp = float(split_data[3])

	def __str__(self):
		return ("IAMAT " + str(self.client_id) + " " + str(self.gps) + " " + str(self.timestamp))

class WHATSAT:
	def __init__(self, data):
		# WHATSAT <client id> <radius> <upper bound>
		# WHATSAT kiwi.cs.ucla.edu 10 5
		split_data = data.split(" ")
		self.client_id = split_data[1]
		self.radius = split_data[2]
		self.upper_bound = split_data[3]

	def __str__(self):
		return ("WHATSAT " + str(self.client_id) + " " + str(self.radius) + " " + str(self.upper_bound))	

class AT:
	def __init__(self, server_id, time_elapsed, client_id, gps, timestamp):
		self.server_id = server_id
		self.time_elapsed = time_elapsed
		self.client_id = client_id
		self.gps = gps
		self.timestamp = float(timestamp)

	def __str__(self):
		return ("AT " + str(self.server_id) + " " + str(self.time_elapsed) + " " + str(self.client_id) + " " + str(self.gps) + " " + str(self.timestamp))

	# Construct AT from an AT message
	@classmethod
	def from_client(cls, data):
		# AT <server id> <time elapsed since time client sent message> <client id> <gps coordinates> <client timestamp>
		# AT Goloman +0.263873386 kiwi.cs.ucla.edu +34.068930-118.445127 1520023934.918963997
		split_data = data.split(" ")
		cls(split_data[1], split_data[2], split_data[3], split_data[4], split_data[5])
		# self.server_id = split_data[1]
		# self.time_elapsed = split_data[2]
		# self.client_id = split_data[3]
		# self.gps = split_data[4]
		# self.timestamp = split_data[5]

	# Construct AT as a response to a IAMAT
	@classmethod
	def from_iamat(cls, iamat, server_id, time_elapsed):
		# IAMAT <client id>	<gps coordinates> <time client sent message>
		# AT <server id> <time elapsed since time client sent message> <client id> <gps coordinates> <client timestamp>
		return cls(server_id=server_id, time_elapsed=time_elapsed, client_id=iamat.client_id, gps=iamat.gps, timestamp=iamat.timestamp)


def is_iamat(data):
	try:
		split_data = data.split(" ")
		if (len(data) >= 5) and (len(split_data) == 4):
			if split_data[0] == "IAMAT":
				float(split_data[3])
				return True
	except Exception:
		return False
	return False

def is_whatsat(data):
	if (len(data) >= 7) and (len(data.split(" ")) == 4):
		if data[0:7] == "WHATSAT":
			return True
	return False



# Creates a server
def main():
	# Process CLI arguments
	if len(sys.argv) is 2:
		server_id = sys.argv[1]
		print("Server ID: " + server_id)
	else:
		print("Usage: python3 server.py <server_id>")
		sys.exit()



	# Goloman talks with Hands, Holiday and Wilkes.
	# Hands talks with Wilkes.
	# Holiday talks with Welsh and Wilkes.

	# A server should accept TCP connections from clients
	# A server should handle IAMAT messages from clients
	# A server should handle WHATSAT messages from clients

	# Create a socket
	# socket.socket(family=AF_INET, type=SOCK_STREAM, proto=0, fileno=None)
	# AF_INET means IPv4 addresses
	# SOCK_STREAM means TCP connection

# 804-610-791	11859	11867

	if server_id == 'Goloman':
		port = 11861
	elif server_id == 'Hands':
		port = 11862
	elif server_id == 'Holiday':
		port = 11863
	elif server_id == 'Welsh':
		port = 11864
	elif server_id == 'Wilkes':
		port = 11865
	else:
		print("Usage: python3 server.py <server_id>, where <server_id> must be one of Goloman, Hands, Holiday, Welsh, Wilkes")
		sys.exit()

	HOST = '127.0.0.1'

	SERVER_IP = (HOST, port)

	# Open Socket
	with socket.socket() as s:
		s.bind(SERVER_IP)  # associate application's socket with an IP address
		print("Listening for incoming connections.")
		s.listen()  # Listen for incoming connections
		print("Accepting incoming connection.")
		conn, address = s.accept()  # Accept an incoming connection

		# Open Connection
		with conn:
			print("Accepted incoming connection from ", address)
			while True:
				# Decode data received from socket
				data = conn.recv(1024).decode('utf-8')  # Receive 1024 bytes from connection
				print(data)

				if is_iamat(data):
					# Server receives IAMAT message


					# Parse 
					iamat = IAMAT(data)
					print("Received IAMAT: ", iamat)

					# Record time elapsed
					print(iamat.timestamp, time.time())
					time_elapsed = time.time() - iamat.timestamp

					# Reply with AT message
					at = AT.from_iamat(iamat=iamat, server_id=server_id, time_elapsed=time_elapsed)
					print("Sending AT: ", at)
					conn.sendall(at.__str__().encode('utf-8'))

				elif is_whatsat(data):
					# Server receives WHATSAT message

					print("Received WHATSAT")
					# Parse
					whatsat = WHATSAT(data)

					# Make API request to Google Places



				# invalid command
				else:
					conn.sendall(('? ' + data).encode('utf-8'))


if __name__ == "__main__":
	main()


# If Client sends an IAMAT message to Server
# IAMAT <client id>	<gps coordinates> <time client sent message>
# Server responds with
# AT <server id> <time elapsed since time client sent message> <client id> <client timestamp>

# Ex:
# IAMAT kiwi.cs.ucla.edu +34.068930-118.445127 1520023934.918963997
# AT Goloman +0.263873386 kiwi.cs.ucla.edu +34.068930-118.445127 1520023934.918963997

# If Client sends an WHATSAT message to Server
# WHATSAT <client id> <radius> <upper bound>
# 

