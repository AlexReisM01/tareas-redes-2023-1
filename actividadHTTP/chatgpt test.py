import socket
import json

# Load the JSON file
with open('censored.json', 'r') as f:
    config = json.load(f)

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a local host and port
server_socket.bind(('localhost', 8000))

# Listen for incoming connections
server_socket.listen(3)

while True:
    # Accept a connection
    client_socket, client_address = server_socket.accept()

    # Receive the request from the client
    request = client_socket.recv(1024).decode()

    # Split the request into its components
    method, url, version = request.split('\n')[0].split()

    # Check if the URL is in the blocked list
    blocked = False
    for blocked_url in config["blocked"]:
        if blocked_url in url:
            blocked = True
            break

    if blocked:
        # Return a 403 error if the URL is blocked
        response = 'HTTP/1.1 403 Forbidden\n\n'
        client_socket.sendall(response.encode())
        client_socket.close()
    else:
        # Replace the specified words in the URL
        #for dic in config["forbidden_words"]:
        #    for word in dic.keys():
        #        replacement = dic[word]
                

        # Connect to the server and send the request
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        url = url.split('://')
        url = url[1]
        url, _ = url.split('/')
        server_socket.connect((url, 80))
        server_socket.send(request.encode())

        # Receive the response from the server and send it back to the client
        response = server_socket.recv(1024)
        client_socket.sendall(response)

        # Close the sockets
        server_socket.close()
        client_socket.close()