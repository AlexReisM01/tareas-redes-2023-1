import socket
import json
import sys


def receive_header(connection_socket, buff_size, end_sequence):
    """
    this function receives the header of the messagee, and some of the body if necessary
    """
    # recibimos la primera parte del mensaje
    recv_message = connection_socket.recv(buff_size)
    full_head = recv_message.decode()
    
    # verificamos si llegó el mensaje completo o si aún faltan partes del mensaje
    is_end_of_message = "\r\n\r\n" in full_head

    # entramos a un while para recibir el resto y seguimos esperando información
    # mientras el buffer no contenga secuencia de fin de mensaje
    while not is_end_of_message:
        # recibimos un nuevo trozo del mensaje
        recv_message = connection_socket.recv(buff_size)
        
        # lo) añadimos al mensaje "completo"
        full_head += recv_message.decode()

        # verificamos si es la última parte del mensaje
        if("\r\n\r\n" in full_head):
            break

    
    head, body = full_head.split("\r\n\r\n")
    # removemos la secuencia de fin de mensaje, esto entrega un mensaje en string
    

    header_str = head
    header_list = header_str.split("\r\n")
    first_line = header_list[0]
    header_dict = dict()
    header_dict["Content-Length"] = '0'
    for header in header_list[1:]:
        header_split = header.split(": ")
        header_dict[header_split[0]] = header_split[1]
     
    # finalmente retornamos el mensaje
    return header_dict, first_line, body

def receive_body(connection_socket, buff_size, content_length):
    """ 
    This function returns a string of the rest of the body of the message
    """

    if content_length == 0:
        return ""
    
    recv_message = connection_socket.recv(min(buff_size, content_length))
    full_body = recv_message
    content_length-=buff_size

    while buff_size <= content_length:
        recv_message = connection_socket.recv(buff_size)
        full_body+=recv_message
        content_length-=buff_size
    if content_length>0:
        recv_message = connection_socket.recv(content_length)
        full_body+=recv_message
    return full_body.decode()

def dict_to_str(head, first_line):
    """
    this transforms the header dictionary to a string
    """
    header = first_line
    for key in head.keys():
                header+= "\r\n" + key + ': ' + head[key]
    return header





if __name__ == "__main__": 
    # definimos el tamaño del buffer de recepción y la secuencia de fin de mensaje
    buff_size = 32
    end_of_message = "\r\n\r\n"
    new_socket_address = ('localhost', 8000)

    print('Creando socket - Servidor')
    # armamos el socket
    # los parámetros que recibe el socket indican el tipo de conexión
    # socket.SOCK_STREAM = socket orientado a conexión
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # le indicamos al server socket que debe atender peticiones en la dirección address
    # para ello usamos bind
    server_socket.bind(new_socket_address)

    # luego con listen (función de sockets de python) le decimos que puede
    # tener hasta 3 peticiones de conexión encoladas
    # si recibiera una 4ta petición de conexión la va a rechazar
    server_socket.listen(3)

    # nos quedamos esperando a que llegue una petición de conexión
    print('... Esperando clientes')
    
    with open(sys.argv[1]) as file:
        json_data = json.load(file)
    blocked = json_data["blocked"]
    words = json_data["forbidden_words"]
    user = json_data["user"]

    
    while True:
        # cuando llega una petición de conexión la aceptamos
        # y se crea un nuevo socket que se comunicará con el cliente
        new_socket, new_socket_address = server_socket.accept()

        # luego recibimos el mensaje usando la función que programamos
        # esta función entrega el mensaje en string (no en bytes) y sin el end_of_message
        get_head, get_first_line, body = receive_header(new_socket, buff_size, end_of_message)
        get_content_length = int(get_head["Content-Length"])
        l = len(body)
        get_body = body + receive_body(new_socket, buff_size, get_content_length - l)
        get_head["X-ElQuePregunta"] = user
        get_head_str = dict_to_str(get_head, get_first_line)
        uri = get_first_line.split(" ")[1]
        if(uri in blocked):
            response_message = "HTTP/1.1 403 Que querias ver?\r\n\r\n 403 no se puede\r\n"
        else:
            get_message = get_head_str + "\r\n\r\n" + get_body
            get_message = get_message.encode()
            address = uri.split("://")[1]
            address = address.split('/')[0]
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                client_socket.connect((address, 80))

                client_socket.send(get_message)
                response_head, response_first_line, body = receive_header(client_socket, buff_size, end_of_message)
                
                response_content_length = int(response_head["Content-Length"])
                l = len(body)
                response_body = body + receive_body(client_socket, buff_size, response_content_length - l)

                for word in words:
                    for key in word.keys():
                       response_body = response_body.replace(key, word[key])
                response_head["Content-Length"] = str(len(response_body.encode('utf-8')))
                response_head_str = response_first_line
                response_head_str = dict_to_str(response_head, response_first_line)
                response_message = response_head_str + "\r\n\r\n" + response_body
                client_socket.close()
            except:
                response_message = "HTTP/1.1 404 Not found\r\n\r\n 404 not found\r\n"
        
        
        # el mensaje debe pasarse a bytes antes de ser enviado, para ello usamos encode
        new_socket.send(response_message.encode('utf-8'))
            
        # cerramos la conexión
        # notar que la dirección que se imprime indica un número de puerto distinto al 5000
        new_socket.close()
        
        print(f"conexión con {new_socket_address} ha sido cerrada")

        # seguimos esperando por si llegan otras conexiones