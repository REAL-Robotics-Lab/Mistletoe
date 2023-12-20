import socket
import time
from random import randrange
import pickle

import json

class WSClient():
    data: dict[dict[str, str]]

    def __init__(self, hostname: str, port: int=5000) -> None:
        port = 5000  # socket server port number

        self.data = {
            "main" : {}
        }

        self.client_socket = socket.socket()  # instantiate
        self.client_socket.connect((hostname, port))  # connect to the server

    def send_custom_data(self, data: dict):
        sent_data = pickle.dumps(data)
        self.client_socket.send(sent_data)
        # self.client_socket.recv(1024)  # receive response
    
    def send_telemetry(self):
        self.send_custom_data(self.data)

    def close_connection(self):
        self.client_socket.close()  # close the connection
    
    def add_data(self, table: str, variable: str, data: str):
        if table not in self.data.keys():
            self.data[table] = dict()
        
        self.data[table][variable] = data

if __name__ == '__main__':
    ws_client = WSClient(hostname=input("Enter hostname: "),port=5000)
    print("connected")

    for i in range(500):
        ws_client.data = {
            "main": {
                "x": str(i),
                "real_pos": str(1),
                "desired_pos": str(-1)
            }
        }
        ws_client.send_telemetry()
        time.sleep(0.01)
    ws_client.close_connection()