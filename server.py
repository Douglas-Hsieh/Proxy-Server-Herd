import sys	# CLI arguments
import socket
import json
import time
import aiohttp  # Asynchronous IO with HTTP
import asyncio  # Asynchronous Python programming
import re  # Regular Expressions

class IAMAT:
	# Parse IAMAT formatted data
	def __init__(self, data):
		# IAMAT <client id>	<gps coordinates> <time client sent message>
		# IAMAT kiwi.cs.ucla.edu +34.068930-118.445127 1520023934.918963997
		split_data = data.split(" ")
		self.client_id = str(split_data[1])
		self.gps = str(split_data[2])
		self.timestamp = float(split_data[3])

		# Get latitude, longitude
		abs_lat_lng = [x for x in re.split('\+|\-', self.gps) if x != '']
		sign_lat_lng = [x for x in re.split('[0-9]|\.', self.gps) if x != '']
		self.lat = float(sign_lat_lng[0] + abs_lat_lng[0])
		self.lng = float(sign_lat_lng[1] + abs_lat_lng[1])


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


# class Client_Location:
# 	@staticmethod
# 	def add_location():

# 			client_locations[iamat.client_id] = iamat.lat, iamat.lng


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
	try:
		split_data = data.split(" ")
		if (len(data) >= 7) and (len(split_data) == 4):
			radius = float(split_data[2])
			upper_bound = int(split_data[3])
			if data[0:7] == "WHATSAT" and radius >= 0 and radius <= 50 and upper_bound >= 0 and upper_bound <= 20:
				return True
	except Exception:
		return False
	return False


def get_nearby_search_url(api_key, lat, lng, radius):
	return ('https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
	+ '&key=' + str(api_key)
	+ '&location=' + str(lat) + ',' + str(lng)
	+ '&radius=' + str(radius))


# Make a nearby search request on Google Places API
# Return nearby_search result
async def nearby_search(session, url, upper_bound):
	async with session.get(url) as response:
		return (await response.text())


# server defines behavior for handling each open_connection

# Echo data back to client
async def echo_server(reader, writer):

	while True:
		data = await reader.read(1024)
		if not data:  # Handles non-data, such as when client closes connection
			break
		print("Received: ", data.decode())
		print("Sending: ", data.decode())
		writer.write(data)
		await writer.drain()
	writer.close()


# Implementation of an instance of a server response to a client
async def my_server(reader, writer, server_id, api_key, client_locations):

	# client_locations = {}  # client_location[client_id] == (lat, lnd)

	while True:
		encoded_data = await reader.read(1024)

		# Handle if client stops sending data
		if not encoded_data:
			break

		data = encoded_data.decode()

		# Client shares location
		if is_iamat(data):
			iamat = IAMAT(data)

			# Store client location
			client_locations[iamat.client_id] = iamat.lat, iamat.lng

			# Record time elapsed
			print(iamat.timestamp, time.time())
			time_elapsed = time.time() - iamat.timestamp

			# Send AT message to client
			at = AT.from_iamat(iamat, server_id, time_elapsed)
			writer.write(at.__str__().encode())
		# Client wants information about the location of a client
		elif is_whatsat(data):
			whatsat = WHATSAT(data)

			client_id = whatsat.client_id
			radius = whatsat.radius
			upper_bound = whatsat.radius

			if client_locations.get(client_id):
				# server knows about client location
				lat, lng = client_locations[client_id]
				# Query Google Places API
				url = get_nearby_search_url(api_key, lat, lng, radius)
				# TODO: query google places api, make things async, communicate between servers
				print('URL: ', url)

				async with aiohttp.ClientSession() as session:
					search_result = await nearby_search(session, url, upper_bound)

				# Write search result back to client
				writer.write(search_result.encode())

			else:
				# server doesn't know this client location, command fails
				writer.write(('? ' + data).encode())
		else:
			writer.write(('? ' + data).encode())

		await writer.drain()
	# connection dropped, close the writer
	writer.close()



async def main():

	API_KEY = 'AIzaSyCjsE3QvP9vF8oh5F5TDuCmpJH2oG4Tsfw'

	# Example request URL
	'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=UCLA&inputtype=textquery&key=AIzaSyCjsE3QvP9vF8oh5F5TDuCmpJH2oG4Tsfw'

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

	# 11859	11867

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

	server_ip_address = (HOST, port)
	client_locations = {}  # client_locations is a reference to a empty dict, {} is an immutable empty dict
	server = await asyncio.start_server(lambda reader, writer: my_server(reader, writer, server_id, API_KEY, client_locations),
		HOST, port)
	await server.serve_forever()  # Handle client connections







	# # Open Socket
	# with socket.socket() as s:
	# 	s.bind(SERVER_IP)  # associate application's socket with an IP address
	# 	print("Listening for incoming connections.")
	# 	s.listen()  # Listen for incoming connections
	# 	print("Accepting incoming connection.")
	# 	conn, address = s.accept()  # Accept an incoming connection

	# 	# Open Connection
	# 	with conn:
	# 		print("Accepted incoming connection from ", address)
	# 		while True:
	# 			# Decode data received from socket
	# 			data = conn.recv(1024).decode('utf-8')  # Receive 1024 bytes from connection
	# 			print(data)

	# 			if is_iamat(data):
	# 				# Server receives IAMAT message


	# 				# Parse 
	# 				iamat = IAMAT(data)
	# 				print("Received IAMAT: ", iamat)

	# 				# Record time elapsed
	# 				print(iamat.timestamp, time.time())
	# 				time_elapsed = time.time() - iamat.timestamp

	# 				# Reply with AT message
	# 				at = AT.from_iamat(iamat=iamat, server_id=server_id, time_elapsed=time_elapsed)
	# 				print("Sending AT: ", at)
	# 				conn.sendall(at.__str__().encode('utf-8'))

	# 			elif is_whatsat(data):
	# 				# Server receives WHATSAT message

	# 				print("Received WHATSAT")
	# 				# Parse
	# 				whatsat = WHATSAT(data)

	# 				# Make API request to Google Places

	# 			# invalid command
	# 			else:
	# 				conn.sendall(('? ' + data).encode('utf-8'))


if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	# loop.set_debug(True)
	# asyncio.run(main())
	loop.run_until_complete(main())


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

