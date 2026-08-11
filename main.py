import socket
import datetime

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((SERVER_HOST, SERVER_PORT))

server_socket.listen(5)

print(f"Listening on port {SERVER_PORT} ...")

while True:
    client_socket, client_address = server_socket.accept()
    request = client_socket.recv(1500).decode(encoding="utf")
    print(request)
    reqHeaders = request.split('\n')
    reqFirstLine = reqHeaders[0].split()

    httpMethod = reqFirstLine[0]
    reqPath = reqFirstLine[1]
    httpVersion = reqFirstLine[2]
    ifModifiedFlag = False
    AuthFlag = False

    password = ""
    adminBearer = "admin123"
    studentBearer = "student321"

    modifiedSince = datetime.datetime(month=9,day=20,year=2026)  
    modifiedSinceString = datetime.datetime.strftime(modifiedSince, ' %a, %d %b %Y %H:%M:%S GMT')
    currentDate = datetime.datetime.strftime(datetime.datetime.now(), ' %a, %d %b %Y %H:%M:%S GMT')

    for line in reqHeaders:
        if "If-Modified-Since:" in line:
            ifModifiedTimestamp = line.replace("If-Modified-Since:", "")
            timestampDateTime = datetime.datetime.strptime(ifModifiedTimestamp, ' %a, %d %b %Y %H:%M:%S GMT\r') 

            ifModifiedFlag = True   
        elif "Authentication: Bearer" in line:
            password = line.replace("Authentication: Bearer ", "").strip()
            AuthFlag = True


    if httpVersion != "HTTP/1.1":
        response = 'HTTP/1.1 505 HTTP Version Not Supported \n\n'
    elif httpMethod == "GET":
        getResponseHeaders = 'Date:' + currentDate + '\nExpires: ' + modifiedSinceString + '\n' + 'Transfer-Encoding: chunked \n'

        if ifModifiedFlag and (modifiedSince < timestampDateTime):
            response = 'HTTP/1.1 304 Not Modified \n' + getResponseHeaders
        elif reqPath == '/test.html':
            page = open('test.html')
            content = page.read()
            page.close()

            response = 'HTTP/1.1 200 OK \n\n' + getResponseHeaders + content
        elif reqPath == '/adminonly.html':
            if AuthFlag and password == adminBearer:
                page = open('adminonly.html')
                content = page.read()
                page.close()

                response = 'HTTP/1.1 200 OK \n\n' + getResponseHeaders + content   
            elif AuthFlag and password == studentBearer:
                response = 'HTTP/1.1 403 Forbidden \n\n Date:' + currentDate + '\n'
            else:
                response = 'HTTP/1.1 404 Not Found \n\n'
        else:
            response = 'HTTP/1.1 404 Not Found \n\n'
    else:
        response = 'HTTP/1.1 405 Method Not Allowed \n\n'
    client_socket.sendall(response.encode(encoding="utf"))
    client_socket.close()



