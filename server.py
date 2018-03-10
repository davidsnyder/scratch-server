import socket
import os

HOST = "127.0.0.1"
PORT = 9000
SERVER_ROOT = os.path.abspath("www")

HTML_BODY_200 = "<h1>Hello!</h1>"
HTML_BODY_400 = "Bad Request"
HTML_BODY_404 = "Not Found"
HTML_BODY_405 = "Method Not Allowed"

FILE_HEADERS = """\
HTTP/1.1 200 OK
Content-type: {content_type}
Content-length: {content_length}

"""

OK_RESPONSE = f"""\
HTTP/1.1 200 OK
Content-type: text/html
Content-length: {len(HTML_BODY_200)}

{HTML_BODY_200}""".encode('ASCII')

BAD_REQUEST_RESPONSE = f"""\
HTTP/1.1 400 Bad Request
Content-type: text/plain
Content-length: {len(HTML_BODY_400)}

{HTML_BODY_400}""".encode('ASCII')

NOT_FOUND_RESPONSE = f"""\
HTTP/1.1 404 Not Found
Content-type: text/plain
Content-length: {len(HTML_BODY_404)}

{HTML_BODY_404}""".encode('ASCII')

METHOD_NOT_ALLOWED_RESPONSE = f"""\
HTTP/1.1 405 Method Not Allowed
Content-type: text/plain
Content-length: {len(HTML_BODY_405)}

{HTML_BODY_405}""".encode('ASCII')

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
				request = {"method": method, "path": path, "headers": headers}
				print(request)
				if request['method'] != "GET":
					client_sock.sendall(METHOD_NOT_ALLOWED_RESPONSE)
				else:
					path = request['path']
					if path == "/":
						path = "/index.html"
					filename = SERVER_ROOT + path

					if os.path.isfile(filename):
						file = open(filename, 'rb')
						response_headers = FILE_HEADERS.format(content_type="text/html", content_length=os.path.getsize(filename)).encode('ASCII')
						client_sock.sendall(response_headers)
						client_sock.sendfile(file)
					else:
						client_sock.sendall(NOT_FOUND_RESPONSE)
					client_sock.close()
			except Exception as e:
				print(f'Failed to parse request: {e}')
				client_sock.sendall(BAD_REQUEST_RESPONSE)
