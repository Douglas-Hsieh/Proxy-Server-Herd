import asyncio
import time

async def client():

	host = '127.0.0.1'
	port = 11861

	server_ip_address = (host, port)

	reader, writer = await asyncio.open_connection(host, port)

	# for i in range(0, 5):
	# 	msg = 'Hello World!'
	# 	print('Sending: ', msg)
	# 	writer.write(msg.encode())

	# 	data = await reader.read(1024)
	# 	print('Received: ', data.decode())

	# 	await asyncio.sleep(1)


	# Send IAMAT
	current_time = time.time()

	msg = 'IAMAT kiwi.cs.ucla.edu +34.068930-118.445127 ' + str(current_time)
	print('Sending: ', msg)
	writer.write(msg.encode())
	data = await reader.read(1024)
	print('Received: ', data.decode())
	writer.close()
	await writer.wait_closed()

	# # Create socket
	# with socket.socket() as s:
	# 	# Connect to a server
	# 	s.connect(server_ip_address)

	# 	while True:
	# 		msg = "herro"
	# 		s.sendall(msg.encode('utf-8'))
	# 		data = s.recv(1024).decode('utf-8')
	# 		print("Received: ", data)


if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.run_until_complete(client())




