# cited from these tutorials
# https://alexanderell.is/posts/simple-cache-server-in-python/
# https://www.geeksforgeeks.org/python/creating-a-proxy-webserver-in-python-set-1/
import socket

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8081

cache = {}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(5)

print(f"Cache Proxy is watching on port {SERVER_PORT} ...")

while True:
    # same processing as main web server
    client_socket, client_address = server_socket.accept()
    request = client_socket.recv(1500).decode(encoding="utf")
    reqHeaders = request.split('\n')
    reqFirstLine = reqHeaders[0].split()
    httpMethod = reqFirstLine[0]
    reqPath = reqFirstLine[1]

    if "://" not in reqPath:
        # Not absolute form URI, send back 400
        client_socket.sendall(b'HTTP/1.1 400 Bad Request \n\n')
        client_socket.close()
        continue

    if reqPath in cache:
        # Requested Object is in Cache! Return object to Client
        print("Request in Cache: ", reqPath)
        client_socket.sendall(cache[reqPath])
    else:
        # Send Request to Origin Server for Client's Request
        print("Request not in Cache, fetch from Origin: ", reqPath)
        scheme, rest = reqPath.split("://", 1)
        hostAndPort, path = rest.split("/", 1)
        path = "/" + path

        if ":" in hostAndPort:
            originHost, originPort = hostAndPort.split(":", 1)
            originPort = int(originPort)
        else:
            originHost, originPort = hostAndPort, 80

        originSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        originSocket.connect((originHost, originPort))
        originSocket.sendall(("GET " + path + " HTTP/1.1\r\nHost: " + originHost + "\r\nConnection: close\r\n\r\n").encode())

        originResponse = b""
        while True:
            chunk = originSocket.recv(1500)
            if not chunk:
                break
            originResponse = originResponse + chunk
        originSocket.close()

        cache[reqPath] = originResponse
        client_socket.sendall(originResponse)

    client_socket.close()