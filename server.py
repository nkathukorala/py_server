import os
import socket
import subprocess


base="htdocs"

def phpObj(data):

    php_string = "$data = array(\n"

    for v in data:
        php_string += f"    '{v[0]}' => '{v[1]}',\n"

    php_string += ");"

    return php_string



def webserver(host, port):
    temp_file_location = ''
    parameters = ''

    print(host)
    print(port)
    websocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print(websocket)
    websocket.bind((host,port))
    websocket.listen(5)
    print("Server is running on http://"+host+":"+str(port))
    
    while True:
        temp_file_location = ''
        parameters = ''

        connection, address = websocket.accept()
        # print(connection)
        # print(connection.recv(1024))
        # print(connection.recv(1024).decode("utf-8").split("\r\n"))
        req_lines = connection.recv(4096).decode("utf-8").split("\r\n")
        path =  req_lines[0].split(" ")[1]

        # print(path)
        if 1 < len(path.split("?")):   # get request URL parameters 
            path,parameters = path.split("?")
            # print(parameters)


        req_type = req_lines[0].split(" ")[0]
        # print(req_lines)
        file_location = os.path.join(base, path.lstrip("/"))
        # print(os.path.commonpath([base, file_location]))
        if os.path.exists(file_location) and os.path.commonpath([base, file_location]) == base:
            # print(file_location)
            if os.path.isdir(file_location):
                if os.path.exists(os.path.join(file_location,"index.php")):
                    file_location = os.path.join(file_location,"index.php")
                elif os.path.exists(os.path.join(file_location,"index.html")):
                    file_location = os.path.join(file_location,"index.html")
                
            # print(file_location)
            if not(os.path.isdir(file_location)):
                if file_location.endswith(".php"):

                    if req_type == "POST":

                        post_data = req_lines[req_lines.index('')+1].split("&")
                        post_data = list(map(lambda x: [ it for it in x.split("=")],post_data ))
                        print(post_data)

                        # print(phpObj(post_data))

                        php_text = "<?php " + phpObj(post_data) + "\n $_POST = $data; ?> "
                        # print(php_text)




                        with open(file_location, 'r') as php_file:
                            php_code = php_file.read()


                        
                        directory_path = os.path.dirname(file_location)
                        file_name = "." + "temp" + "_" + os.path.basename(file_location)
                        file_location = os.path.join(directory_path,file_name)
                        temp_file_location = file_location


                        with open(file_location, 'w') as php_file:
                            php_file.write(php_text + php_code)


                    if req_type == "GET" and parameters: 
                        get_data = parameters.split("&")
                        get_data = list(map(lambda x: [ it for it in x.split("=")], get_data))  

                        php_text = "<?php " + phpObj(get_data) + "\n $_GET = $data; ?> "

                        with open(file_location, 'r') as php_file:
                            php_code = php_file.read()

                        directory_path = os.path.dirname(file_location)
                        file_name = "." + "temp" + "_" + os.path.basename(file_location)
                        file_location = os.path.join(directory_path, file_name)
                        temp_file_location = file_location

                        with open(file_location, 'w') as php_file:
                            php_file.write(php_text + php_code)


                        # print(post_data)

                    try:
                        output = subprocess.run(['php',file_location], capture_output=True, text=True, check=True)
                        response = "HTTP/1.1 200 OK\r\n\r\n" + output.stdout
                    
                    except subprocess.CalledProcessError as e:
                        response = "HTTP/1.1 500 Internal Server Error\r\n\r\nInternal Server Error\n"  + e.stderr
                    
                    if temp_file_location:   # Delete temporary file 
                        try:
                            os.remove(temp_file_location)
                            print(f"File '{temp_file_location}' has been deleted.")
                        except OSError as e:
                            print(f"Error deleting file: {e}")

                else:
                    try:
                        with open(file_location, "rb") as file:
                            output = file.read()
                            response = "HTTP/1.1 200 OK\r\n\r\n" + output.decode("utf-8")
                   
                    except Exception as e:
                        response = "HTTP/1.1 500 Internal Server Error\r\n\r\n" + str(e)
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\nFile Not Found" 

        else:
            response = "HTTP/1.1 403 Forbidden\r\n\r\nForbidden"

        connection.sendall(response.encode("utf-8"))

        connection.close()



host = "127.0.0.1"
port = 2728


webserver(host, port)


