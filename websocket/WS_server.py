import socket
import pickle
import json
from threading import Thread
from random import randrange

# get the hostname
# host = socket.gethostname()
host = '192.168.1.129'
port = 5000  # initiate port no above 1024

server_socket = socket.socket()  # get instance
server_socket.settimeout(30000)
# look closely. The bind() function takes tuple as argument
server_socket.bind((host, port))  # bind host address and port together

# configure how many client the server can listen simultaneously
server_socket.listen(2)
conn, address = server_socket.accept()  # accept new connection
print("connected")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import time
style.use('fivethirtyeight')


max_len = 10

data = {
            "main": {
                "timestamp": str(0),
            },
            "motor_11": {
                "Position": str(randrange(-10,10)),
                "Desired Position": str(randrange(-10,10))
            }
        }

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

x = []
y_1 = []
y_2 = []


def animate(i):

    global x
    global y_1
    global y_2
    global data

    counter = float(data["main"]["timestamp"])
    real_pos = float(data["motor_11"]["Position"])
    desired_pos = float(data["motor_11"]["Desired Position"])

    x.append(counter)
    y_1.append(desired_pos)
    y_2.append(real_pos)

    items_per_frame = 10

    if x[-1] > items_per_frame:
        x_up_bound = x[-1]
    else: 
        x_up_bound = items_per_frame
    x_low_bound = x[-1] - items_per_frame

    ax1.clear()
    ax1.plot(x, y_1, color='red')
    ax2 = ax1.twinx()
    ax2.plot(x, y_2, color='blue')

    a,b = -10, 10
    ax1.set_ylim(a,b)
    ax2.set_ylim(a,b)
    ax1.set_xlim(x_low_bound, x_up_bound)
    ax2.set_xlim(x_low_bound, x_up_bound)

    # print(x) 

def render_animation(): 
    ani = animation.FuncAnimation(fig, animate, interval=10)
    plt.show()

def get_data_socket():
    global data

    for i in range(500):
        # receive data stream. it won't accept data packet greater than 1024 bytes
        data_preprocessed = conn.recv(1024)

        if not data_preprocessed:
            # if data is not received break
            break

        # print(len(data))
        data = pickle.loads(data_preprocessed)
        

        print(data)

        # print("from connected user: " + str(data))
        conn.send('b'.encode())  # send data to the client
    time.sleep(0.01)

socket_thread = Thread(target=get_data_socket)

socket_thread.start()
render_animation()

conn.close()  # close the connection
