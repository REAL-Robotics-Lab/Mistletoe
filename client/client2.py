import socket
import time
from random import randrange


def client_program():
    host = socket.gethostname()  # as both code is running on same pc
    port = 5000  # socket server port number

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server

    for i in range(500):
        random_number = str(randrange(1, 10))     
        client_socket.send(random_number.encode())  # send message
        data = client_socket.recv(1024).decode()  # receive response
        time.sleep(0.01) #100hz

    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()


