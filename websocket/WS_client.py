import socket
import time
from random import randrange
import pickle

import json

class WSClient():

    def __init__(self) -> None:
        host = socket.gethostname()  # as both code is running on same pc
        port = 5000  # socket server port number

        self.client_socket = socket.socket()  # instantiate
        self.client_socket.connect((host, port))  # connect to the server

    def send_data(self, data: dict):
        data = pickle.dumps(data)
        self.client_socket.send(data)
        self.client_socket.recv(1024)  # receive response

    def close_connection(self):
        self.client_socket.close()  # close the connection

if __name__ == '__main__':
    ws_client = WSClient()

    for i in range(500):
        data = {
            "x": str(i),
            "real_pos": str(1),
            "desired_pos": str(-1)
        }
        ws_client.send_data(data)
        time.sleep(0.01)
    ws_client.close_connection()