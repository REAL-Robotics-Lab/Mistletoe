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

# real pos
x_1 = []
x_2 = []
y_1 = []
y_2 = []

# desired pos
# x_3 = []
# x_4 = []
# y_3 = []
# y_4 = []

start_time = time.time()

leg_center_dist_mm_1 = 175.87
leg_center_dist_1 = leg_center_dist_mm_1 / 1000

leg_center_dist_mm_2 = 175.87
leg_center_dist_2 = leg_center_dist_mm_2 / 1000

leg_number = 1

def animate(i):
        
    def calculate_endpoints(formatted_data, leg_number, leg_center_dist_1, leg_center_dist_2):
        
        real_pos_1 = abs(rev_to_radians(float(formatted_data["motor_" + str(leg_number) + "1"]["Position"])))
        desired_pos_1 = abs(rev_to_radians(float(formatted_data["motor_" + str(leg_number) + "1"]["Desired Position"])))

        real_pos_1_x = math.cos(real_pos_1) * leg_center_dist_1
        real_pos_1_y = math.sin(real_pos_1) * leg_center_dist_1

        desired_pos_1_x = math.cos(desired_pos_1) * leg_center_dist_1
        desired_pos_1_y = math.sin(desired_pos_1) * leg_center_dist_1

        real_pos_2 = abs(rev_to_radians(float(formatted_data["motor_" + str(leg_number) + "2"]["Position"])))
        desired_pos_2 = abs(rev_to_radians(float(formatted_data["motor_" + str(leg_number) + "2"]["Desired Position"])))

        real_pos_2_x = math.cos(real_pos_1 + real_pos_2) * leg_center_dist_2
        real_pos_2_y = math.sin(real_pos_1 + real_pos_2) * leg_center_dist_2

        desired_pos_2_x = math.cos(desired_pos_1 + desired_pos_2) * leg_center_dist_2
        desired_pos_2_y = math.sin(desired_pos_1 + desired_pos_2) * leg_center_dist_2

        resultant_desired_pos_x = desired_pos_1_x + desired_pos_2_x
        resultant_desired_pos_y = -desired_pos_1_y - desired_pos_2_y

        resultant_real_pos_x = real_pos_1_x + real_pos_2_x
        resultant_real_pos_y = -real_pos_1_y - real_pos_2_y

        return resultant_desired_pos_x, resultant_desired_pos_y, resultant_real_pos_x, resultant_real_pos_y


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

    # real_pos_1 = abs(rev_to_radians(float(formatted_data["motor_" + str(leg_number) + "1"]["Position"])))
    # desired_pos_1 = abs(rev_to_radians(float(formatted_data["motor_" + str(leg_number) + "1"]["Desired Position"])))

    # real_pos_1_x = math.cos(real_pos_1) * leg_center_dist
    # real_pos_1_y = math.sin(real_pos_1) * leg_center_dist

    # desired_pos_1_x = math.cos(desired_pos_1) * leg_center_dist
    # desired_pos_1_y = math.sin(desired_pos_1) * leg_center_dist

    # real_pos_2 = abs(rev_to_radians(float(formatted_data["motor_" + str(leg_number) + "2"]["Position"])))
    # desired_pos_2 = abs(rev_to_radians(float(formatted_data["motor_" + str(leg_number) + "2"]["Desired Position"])))

    # real_pos_2_x = math.cos(real_pos_1 + real_pos_2) * leg_center_dist
    # real_pos_2_y = math.sin(real_pos_1 + real_pos_2) * leg_center_dist

    # desired_pos_2_x = math.cos(desired_pos_1 + desired_pos_2) * leg_center_dist
    # desired_pos_2_y = math.sin(desired_pos_1 + desired_pos_2) * leg_center_dist

    # resultant_desired_pos_x = desired_pos_1_x + desired_pos_2_x
    # resultant_desired_pos_y =  -desired_pos_1_y - desired_pos_2_y

    # resultant_real_pos_x = real_pos_1_x + real_pos_2_x
    # resultant_real_pos_y = -real_pos_1_y - real_pos_2_y

    resultant_desired_pos_x_1, resultant_desired_pos_y_1, resultant_real_pos_x_1, resultant_real_pos_y_1 = calculate_endpoints(formatted_data, 2, leg_center_dist_1, leg_center_dist_2)
    resultant_desired_pos_x_3, resultant_desired_pos_y_3, resultant_real_pos_x_3, resultant_real_pos_y_3 = calculate_endpoints(formatted_data, 3, leg_center_dist_1, leg_center_dist_2)

    # x_1.append(real_pos_1_x)
    x_1.append(resultant_desired_pos_x_1)
    # y_1.append(real_pos_1_y)
    y_1.append(resultant_desired_pos_y_1)

    # x_3.append(desired_pos_1_x)
    x_2.append(resultant_real_pos_x_1)
    # y_3.append(desired_pos_1_y)
    y_2.append(resultant_real_pos_y_1)

    if len(x_1) > 10:
        x_1.pop(0)
        y_1.pop(0)
        x_2.pop(0)
        y_2.pop(0)

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
    ax2.clear()
    ax1.scatter(x_1, y_1, marker="o", color='red')
    ax2.scatter(x_2, y_2,marker="o", color='blue')
    # ax1.scatter(x_3, y_3,marker="o", color='blue')
    # ax1.scatter(x_4, y_4,marker="o", color='blue')

    # a,b = 0, 0.15
    # ax1.set_ylim(a,b)
    # ax2.set_ylim(a,b)
    
    ax1.set_xlim(-0.15, 0.2)
    ax2.set_xlim(-0.15, 0.2)
    ax1.set_ylim(-0.3, 0.05)
    ax2.set_ylim(-0.3, 0.05)

def render_animation(): 
    anim = animation.FuncAnimation(fig, animate, interval=10)
    plt.show()

socket_thread = Thread(target=get_socket_data)

socket_thread.start()
render_animation()


