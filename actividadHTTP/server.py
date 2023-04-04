import socket
 
 


def receive_header(connection_socket, buff_size, end_sequence):
    """ 
    This function returns a dictionary of all the headers
    """
    # recibimos la primera parte del mensaje
    recv_message = connection_socket.recv(buff_size)
    full_head = recv_message
 
    # verificamos si llegó el mensaje completo o si aún faltan partes del mensaje
    is_end_of_message = contains_end_of_message(full_head.decode(), end_sequence)

    # entramos a un while para recibir el resto y seguimos esperando información
    # mientras el buffer no contenga secuencia de fin de mensaje
    while not is_end_of_message:
        # recibimos un nuevo trozo del mensaje
        recv_message = connection_socket.recv(buff_size)
 
        # lo añadimos al mensaje "completo"
        full_head += recv_message
 
        # verificamos si es la última parte del mensaje
        is_end_of_message = contains_end_of_message(full_head.decode(), end_sequence)
 
    # removemos la secuencia de fin de mensaje, esto entrega un mensaje en string
     
    head = remove_end_of_message(full_head.decode(), end_sequence)
    head = head.decode()
    header_list = header.split("\r\n")
    header_dict = dict()
    header_dict["Content-Length"] = 0
    for header in header_list[1:]:
        header_split = header.split(": ")
        header_dict[header_split[0]] = header_split[1]
     
    # finalmente retornamos el mensaje
    return header_dict

def receive_body(connection_socket, buff_size, content_length):
    """ 
    This function recieves a string of the body
    """
    recv_message = connection_socket.recv(buff_size)
    full_body = recv_message
    
    read_length = buff_size

    while read_length <= content_length:
        recv_message = connection_socket.recv(buff_size)
        full_body+=recv_message
        read_length+=buff_size




def contains_end_of_message(message, end_sequence):
    return message.endswith(end_sequence)

 
def remove_end_of_message(full_message, end_sequence):
    index = full_message.rfind(end_sequence)
    return full_message[:index]
 
if __name__ == "__main__": 
    # definimos el tamaño del buffer de recepción y la secuencia de fin de mensaje
    buff_size = 16
    end_of_message = "\r\n\r\n"
    new_socket_address = ('localhost', 5000)

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
    while True:
        # cuando llega una petición de conexión la aceptamos
        # y se crea un nuevo socket que se comunicará con el cliente
        new_socket, new_socket_address = server_socket.accept()

        # luego recibimos el mensaje usando la función que programamos
        # esta función entrega el mensaje en string (no en bytes) y sin el end_of_message
        head = receive_header(new_socket, buff_size, end_of_message)
        body = 

        print(f' -> Se ha recibido el siguiente mensaje: {recv_message}')

        # respondemos indicando que recibimos el mensaje
        response_message = f"Se ha sido recibido con éxito el mensaje: {recv_message}"

        # el mensaje debe pasarse a bytes antes de ser enviado, para ello usamos encode
        new_socket.send(response_message.encode())

        # cerramos la conexión
        # notar que la dirección que se imprime indica un número de puerto distinto al 5000
        new_socket.close()
        print(f"conexión con {new_socket_address} ha sido cerrada")

        # seguimos esperando por si llegan otras conexiones