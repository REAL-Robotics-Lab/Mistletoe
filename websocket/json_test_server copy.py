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

import math

formatted_data = None

def rev_to_radians(angle_rev):
    return angle_rev * 2 * math.pi

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
                print('received', data.decode().rstrip())
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

# real pos
x_1 = []
x_2 = []
y_1 = []
y_2 = []

# desired pos
x_3 = []
x_4 = []
y_3 = []
y_4 = []

start_time = time.time()

leg_center_dist_mm = 175.87
leg_center_dist = leg_center_dist_mm / 1000

def animate(i):

    global leg_center_dist

    global x_1
    global x_2
    global y_1
    global y_2
    global formatted_data
    global start_time

    if formatted_data == None:
        return

    time_stamp = float(formatted_data["main"]["timestamp"]) - start_time 
    
    points_per_frame = 10

    real_pos_1 = float(formatted_data["motor_11"]["Position"])
    desired_pos_1 = float(formatted_data["motor_11"]["Desired Position"])

    real_pos_1_x = math.cos(rev_to_radians(real_pos_1)) * leg_center_dist
    real_pos_1_y = math.sin(rev_to_radians(real_pos_1)) * leg_center_dist

    desired_pos_1_x = math.sin(rev_to_radians(desired_pos_1)) * leg_center_dist
    desired_pos_1_y = math.sin(rev_to_radians(desired_pos_1)) * leg_center_dist

    real_pos_2 = float(formatted_data["motor_12"]["Position"])
    desired_pos_2 = float(formatted_data["motor_12"]["Desired Position"])

    real_pos_2_x = math.cos(rev_to_radians(real_pos_2)) * leg_center_dist
    real_pos_2_y = math.sin(rev_to_radians(real_pos_2)) * leg_center_dist

    desired_pos_2_x = math.sin(rev_to_radians(desired_pos_2)) * leg_center_dist
    desired_pos_2_y = math.sin(rev_to_radians(desired_pos_2)) * leg_center_dist

    resultant_desired_pos_x = desired_pos_1_x + desired_pos_2_x
    resultant_desired_pos_y = desired_pos_2_y + desired_pos_2_y

    resultant_real_pos_x = real_pos_1_x + real_pos_2_x
    resultant_real_pos_y = real_pos_1_y + real_pos_2_y

    x_1.append(real_pos_1_x)
    x_2.append(resultant_real_pos_x)
    y_1.append(real_pos_1_y)
    y_2.append(resultant_real_pos_y)

    x_3.append(desired_pos_1_x)
    x_4.append(resultant_desired_pos_x)
    y_3.append(desired_pos_1_y)
    y_4.append(resultant_desired_pos_y)

    # if len(x_1) > points_per_frame:
    #     x_1.pop(0)
    #     x_2.pop(0)
    #     x_3.pop(0)
    #     x_4.pop(0)
    #     y_1.pop(0)
    #     y_2.pop(0)
    #     y_3.pop(0)
    #     x_4.pop(0)

    ax1.clear()

    ax1.scatter(x_1, y_1,marker="o", color='red')
    ax1.scatter(x_2, y_2,marker="o", color='red')
    ax1.scatter(x_3, y_3,marker="o", color='blue')
    ax1.scatter(x_4, y_4,marker="o", color='blue')

def render_animation(): 
    anim = animation.FuncAnimation(fig, animate, interval=10)
    plt.show()

socket_thread = Thread(target=get_socket_data)

socket_thread.start()
render_animation()