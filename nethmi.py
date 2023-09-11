import socket
import os
import subprocess

PORT = 2728
ROOT_DIR = 'htdocs'

# Create a socket and bind it to the specified port (IPv4 and TCP)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', PORT))

# Listen for incoming connections
server_socket.listen(1)
print(f'Server listening on port {PORT}')

def php_dict(temp,request_type):
    ans = ""
    value_array = temp[1].split('&')
    for index in value_array:
        x, y = index.split('=')
        ans += f"{request_type}['{x}']={y};"

    ans += "\n"
    return ans

def handle_request(client_socket):
    request_data = client_socket.recv(4096).decode('utf-8')
    request_lines = request_data.split("\r\n")
    file_URL = request_lines[0].split()[1]
    filename = file_URL.split("?")[0]
    print(file_URL)
    
    
    if ("." not in filename):
        if filename.endswith('/'):
            filename += "index.php"
        else:
            filename += "/index.php"

    file_path = os.path.join(ROOT_DIR, *filename.split('/'))
    print(file_path)
    
    if os.path.isfile(file_path):
        if '.php' in filename:
            if request_lines[0].startswith("GET /"):
                request_type = "$_GET"
                split_url = file_URL.split("?")

            elif request_lines[0].startswith("POST /"):
                request_type = "$_POST"
                split_url = [filename, request_lines[-1]]
                
            if len(split_url) > 1:
                elements=php_dict(split_url,request_type)
                
                f = open(file_path, 'r')
                content = f.read()
                f.close()
                
                content = content.replace("<?php", f"<?php \r\n{elements}\r\n")
                
                process = subprocess.Popen(['php8.2\php.exe'], stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                output, error = process.communicate(input=content)
                response = output.encode('utf-8')
                content_type = 'text/html'
            else:  
                with open(file_path, 'rb') as file:
                    response = file.read()
                content_type = 'text/html'

        elif '.html' in filename:
            # rb read binary
            with open(file_path, 'rb') as file:
                response = file.read()
            content_type = 'text/html'
        else:
            with open(file_path, 'rb') as file:
                response = file.read()
            content_type = 'text/plain'
  
        
    # if file dont exist
    else:
        response = b'404 Not Found'
        content_type = 'text/plain'

    # Send HTTP response to the client
    client_socket.sendall(
        f'HTTP/1.1 200 OK\nContent-Type: {content_type}\n\n'.encode('utf-8'))
    # print(response)
    client_socket.sendall(response)

    # Close the client socket
    client_socket.close()
    
    

while True:
    # Accept incoming connections
    client_socket, addr = server_socket.accept()
    print(f'Accepted connection from {addr}')

    # Handle the request from the client
    try:
        handle_request(client_socket)
    except Exception as e:
        print(e)