"""
credit: https://codereview.stackexchange.com/questions/269519/json-packet-transmitter

Server-Side that receives json packets from client over the network using port
5000. Then it saves the json packet to a file with the filename of current time.
"""
import random
import string
from socketserver import StreamRequestHandler, TCPServer
import json
from threading import Thread
import time 

formatted_data = None

class DumpHandler(StreamRequestHandler):

    def handle(self) -> None:
        global formatted_data
        """receive json packets from client"""
        print('connection from {}:{}'.format(*self.client_address))
        try:
            while True:
                data = self.rfile.readline()
                if not data:
                    break
                # print('received', data.decode().rstrip())
                # print(type())
                formatted_data = json.loads(data.decode().rstrip())
        finally:
            print('disconnected from {}:{}'.format(*self.client_address))


def get_socket_data() -> None:
    server_address = ('192.168.1.129', 5000)
    print('starting up on {}:{}'.format(*server_address))
    with TCPServer(server_address, DumpHandler) as server:
        print('waiting for a connection')
        server.serve_forever()

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
style.use('fivethirtyeight')

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax2 = ax1.twinx()
ax3 = ax1.twinx()

x = []
y_1 = []
y_2 = []
y_3 = []

start_time = time.time()

def animate(i):

    global x
    global y_1
    global y_2
    global formatted_data
    global start_time

    if formatted_data == None:
        return

    time_stamp = float(formatted_data["main"]["timestamp"]) - start_time 
    real_pos = float(formatted_data["motor_12"]["Position"])
    desired_pos = -float(formatted_data["motor_12"]["Desired Position"])
    error = desired_pos - real_pos 

    print(real_pos)
    print(desired_pos)

    x.append(time_stamp)
    y_1.append(desired_pos)
    y_2.append(real_pos)
    y_3.append(error)

    second_frame = 10

    x_up_bound = x[-1]
    x_low_bound = x[-1] - second_frame

    ax1.clear()
    ax2.clear()
    ax3.clear()

    ax1.plot(x, y_1, color='red')
    ax2.plot(x, y_2, color='blue')
    ax3.plot(x, y_3, color='green')

    ax1.set_xlim(x_low_bound, x_up_bound)
    ax2.set_xlim(x_low_bound, x_up_bound)
    ax3.set_xlim(x_low_bound, x_up_bound)

    a,b = -1, 1
    ax1.set_ylim(a,b)
    ax2.set_ylim(a,b)
    ax3.set_ylim(a,b)

def render_animation(): 
    anim = animation.FuncAnimation(fig, animate, interval=10)
    plt.show()

socket_thread = Thread(target=get_socket_data)

socket_thread.start()
render_animation()