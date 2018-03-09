import socket

HOST = "127.0.0.1"
PORT = 9000

# RESPONSE_BYTE = b"""\
# HTTP/1.1 200 OK
# Content-type: text/html
# Content-length: 15

# <h1>Hello!</h1>"""

HTML_BODY_200 = "<h1>Hello!</h1>"
HTML_BODY_400 = "Bad Request"

RESPONSE = f"""\
HTTP/1.1 200 OK
Content-type: text/html
Content-length: {len(HTML_BODY_200)}

{HTML_BODY_200}""".encode('ASCII')

BAD_REQUEST_RESPONSE = f"""\
HTTP/1.1 400 Bad Request
Content-type: text/html
Content-length: {len(HTML_BODY_400)}

{HTML_BODY_400}""".encode('ASCII')

with socket.socket() as server_sock:
	#SO_REUSEADDR reuses sockets in a TIME_WAIT state, without waiting for the timeout to expire
	server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_sock.bind((HOST,PORT))
	server_sock.listen(1)
	print(f"Listening on {HOST}:{PORT}...")
	while True:
		client_sock, client_addr = server_sock.accept()
		print(f"Accepted connection from {client_addr}")
		data = client_sock.recv(1024)
		if not data:
			print("Empty request")
		else:
			try:
				lines = data.decode('ASCII').split("\r\n")
				headers = {}
				for index, line in enumerate(lines):
					if not line:
						break
					elif index == 0: #request method
						method, path, _ = line.split(" ")
					else:
						name, _, value = line.partition(":")
						headers[name.lower()] = value.lstrip()
				print({"method": method, "path": path, "headers": headers})
				client_sock.sendall(RESPONSE)
				client_sock.close()
			except Exception as e:
				print(f'Failed to parse request: {e}')
				client_sock.sendall(BAD_REQUEST_RESPONSE)
