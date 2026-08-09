import socket

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((SERVER_HOST, SERVER_PORT))

server_socket.listen(5)

print(f"Listening on port {SERVER_PORT} ...")

while True:
    client_socket, client_address = server_socket.accept()
    request = client_socket.recv(1500).decode()
    print(request)
    reqHeaders = request.split('\n')
    reqFirstLine = reqHeaders[0].split()

    httpMethod = reqFirstLine[0]
    reqPath = reqFirstLine[1]

    if reqPath == '/test.html':
        page = open('test.html')
        content = page.read()
        page.close()

        response = 'HTTP/1.1 200 OK \n\n' + content
        client_socket.sendall(response.encode())
        client_socket.close()