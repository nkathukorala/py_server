import socket
import os
import subprocess

# Define the port to listen on
PORT = 2728

# Define the root directory for serving files
ROOT_DIR = 'htdocs'

def handle_request(client_socket):
    global content_type

    request_data = client_socket.recv(4096).decode('utf-8')
    request_lines = request_data.split("\r\n")
    # print(request_lines)

    # Find file name
    file_URL = request_lines[0].split()[1]
    filename = file_URL.split("?")[0]
    # print(filename)

    # Default to index.php
    # if (".php" not in filename and ".html" not in filename ):
    if ("." not in filename):
        if filename.endswith('/'):
            filename += "index.php"
        else:
            filename += "/index.php"

    

    # find path
    file_path = os.path.join(ROOT_DIR, *filename.split('/'))
    # print(file_path)

    # if file exists
    if os.path.isfile(file_path):
        # Serve PHP file
        if '.php' in filename:
            if request_lines[0].startswith("GET /"):
                request_type = "$_GET"
                split_url = file_URL.split("?")

            elif request_lines[0].startswith("POST /"):
                request_type = "$_POST"
                split_url = [file_path, request_lines[-1]]

            # generate form data and construct an array
            if len(split_url) > 1:
                elements = ""
                value_array = split_url[1].split('&')
                for index in value_array:
                    x, y = index.split('=')
                    elements += f"{request_type}['{x}']={y};"

                elements += "\n"

                f = open(file_path, 'r')
                content = f.read()
                f.close()
                # append the form content
                content = content.replace("<?php", f"<?php \r\n{elements}\r\n")
                print(content)
      
                # execute the command and pass the script content as stdin
                process = subprocess.Popen(['php'], stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                # communicate with the process, passing the PHP script content as input
                output, error = process.communicate(input=content)
                content_type = 'text/html'
                response = output.encode('utf-8')
                client_socket.sendall(
                    f'HTTP/1.1 200 OK\nContent-Type: {content_type}\n\n'.encode('utf-8'))
                # print(response)
                client_socket.sendall(response)

                # Close the client socket
                client_socket.close()
                return
            
            with open(file_path, 'rb') as file:
                response = file.read()
            content_type = 'text/html'
        elif '.html' in filename:
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



# Create a socket and bind it to the specified port (IPv4 and TCP)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', PORT))

# Listen for incoming connections
server_socket.listen(5)
print(f'Server listening on port {PORT}')

while True:
    # Accept incoming connections
    client_socket, addr = server_socket.accept()
    print(f'Accepted connection from {addr}')

    # Handle the request from the client
    try:
        handle_request(client_socket)
    except Exception as e:
        print(e)