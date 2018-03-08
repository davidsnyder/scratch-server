import socket

HOST = "127.0.0.1"
PORT = 9000

# RESPONSE_BYTE = b"""\
# HTTP/1.1 200 OK
# Content-type: text/html
# Content-length: 15

# <h1>Hello!</h1>"""

HTML_BODY = "<h1>Hello!</h1>"

RESPONSE = f"""\
HTTP/1.1 200 OK
Content-type: text/html
Content-length: {len(HTML_BODY)}

{HTML_BODY}""".encode('ASCII')

with socket.socket() as server_sock:
    #SO_REUSEADDR reuses sockets in a TIME_WAIT state, without waiting for the timeout to expire    
	server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_sock.bind((HOST,PORT))
	server_sock.listen(1)
	print(f"Listening on {HOST}:{PORT}...")
	while True:
		client_sock, client_addr = server_sock.accept()
		print(f"Accepted connection from {client_addr}")
		client_sock.sendall(RESPONSE)
		# client_sock.close()

