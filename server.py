import socket
import os
from urllib.parse import unquote_plus

HOST = "127.0.0.1"
PORT = 9000
SERVER_ROOT = os.path.abspath("www")

FAVORITE_FOOD_DATABASE = {
		"Jim" : "ice cream",
		"Bob" : "hamburgers",
		"Mary" : "sushi"
}

HTTP_HEADERS = """\
HTTP/1.1 {response_code} {response_type}
Content-type: {content_type}
Content-length: {content_length}

"""

BAD_REQUEST_RESPONSE_BODY = "Bad Request"
BAD_REQUEST_RESPONSE = HTTP_HEADERS.format(
	response_code=400,
	response_type=BAD_REQUEST_RESPONSE_BODY,
	content_type="text/plain",
	content_length=len(BAD_REQUEST_RESPONSE_BODY)
	) + BAD_REQUEST_RESPONSE_BODY

NOT_FOUND_RESPONSE_BODY = "Not Found"
NOT_FOUND_RESPONSE = HTTP_HEADERS.format(
	response_code=404,
	response_type=NOT_FOUND_RESPONSE_BODY,
	content_type="text/html",
	content_length=len(NOT_FOUND_RESPONSE_BODY)
	) + NOT_FOUND_RESPONSE_BODY

METHOD_NOT_ALLOWED_RESPONSE_BODY = "Method Not Allowed"
METHOD_NOT_ALLOWED_RESPONSE = HTTP_HEADERS.format(
	response_code=405,
	response_type=METHOD_NOT_ALLOWED_RESPONSE_BODY,
	content_type="text/plain",
	content_length=len(METHOD_NOT_ALLOWED_RESPONSE_BODY)
	) + METHOD_NOT_ALLOWED_RESPONSE_BODY

with socket.socket() as server_sock:
	#SO_REUSEADDR reuses sockets in a TIME_WAIT state, without waiting for the timeout to expire
	server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_sock.bind((HOST,PORT))
	server_sock.listen(1)
	print(f"Listening on {HOST}:{PORT}...")
	while True: #SERVER LOOP
		client_sock, client_addr = server_sock.accept()
		print(f"Accepted connection from {client_addr}")
		data = client_sock.recv(1024)
		if not data:
			print("Empty request")
			client_sock.sendall(BAD_REQUEST_RESPONSE)
		else:
			try:
				#PARSE REQUEST
				lines = data.decode('ASCII').split("\r\n")
				request = {"headers": {}}
				for index, line in enumerate(lines):
					if not line:
						break
					elif index == 0: #request method, path, query_parameters
						method, path, _ = line.split(" ")
						request["method"] = method
						path, _, query_parameters = path.partition("?")
						request["path"] = path						
						request["query_parameters"] = {}
						if query_parameters:
							query_parameters = unquote_plus(query_parameters)
							request["query_parameters"] = dict([p.split("=") for p in query_parameters.split("&")])
					else: #headers
						name, _, value = line.partition(":")
						request["headers"][name.lower()] = value.lstrip()
				print(request)
				#END PARSE REQUEST

				#HANDLE REQUEST
				if request['method'] not in ["GET","POST"]:
					client_sock.sendall(METHOD_NOT_ALLOWED_RESPONSE.encode('ASCII'))
				else:
					path = request['path']
					if path == "/":
						path = "/index.html"
					filename = SERVER_ROOT + path

					if os.path.isfile(filename):
						file = open(filename, 'rb')
						if path == "/search.html":
							search_html = file.read()
							name = request["query_parameters"]["name"] if "name" in request["query_parameters"] else ""
							favorite_food = FAVORITE_FOOD_DATABASE[name] if name in FAVORITE_FOOD_DATABASE else "unknown"
							templated_search_html = search_html.decode('utf-8').format(name=name,favorite_food=favorite_food)
							response_headers = HTTP_HEADERS.format(
								response_code=200,
								response_type="OK",
								content_type="text/html",
								content_length=len(templated_search_html)
								).encode('ASCII')
							client_sock.sendall(response_headers)
							client_sock.sendall(templated_search_html.encode('ASCII'))
						else:
							response_headers = HTTP_HEADERS.format(
								response_code=200,
								response_type="OK",
								content_type="text/html",
								content_length=os.path.getsize(filename)
								).encode('ASCII')
							client_sock.sendall(response_headers)
							client_sock.sendfile(file)
					else:
						client_sock.sendall(NOT_FOUND_RESPONSE.encode('ASCII'))
					client_sock.close()
				#END HANDLE REQUEST
			except Exception as e:
				print(f'Failed to parse request: {e}')
				client_sock.sendall(BAD_REQUEST_RESPONSE.encode('ASCII'))
