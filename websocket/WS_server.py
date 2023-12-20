import socket
import pickle
import json

# get the hostname
host = socket.gethostname()
port = 5000  # initiate port no above 1024

server_socket = socket.socket()  # get instance
# look closely. The bind() function takes tuple as argument
server_socket.bind((host, port))  # bind host address and port together

# configure how many client the server can listen simultaneously
server_socket.listen(2)
conn, address = server_socket.accept()  # accept new connection

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import time
style.use('fivethirtyeight')

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

x = []
y_1 = []    
y_2 = []

def animate(i):

    # receive data stream. it won't accept data packet greater than 1024 bytes
    data = conn.recv(1024)

    if not data:
        # if data is not received break
        return

    data = pickle.loads(data)

    print("from connected user: " + str(data))
    conn.send('b'.encode())  # send data to the client

    counter = float(data["x"])
    real_pos = float(data["real_pos"])
    desired_pos = float(data["desired_pos"])

    x.append(counter)
    y_1.append(desired_pos)
    y_2.append(real_pos)
    ax1.clear()
    ax1.plot(x, y_1, color='red')
    ax2 = ax1.twinx()
    ax2.plot(x, y_2, color='blue')

    a,b = -10,10
    ax1.set_ylim(a,b)
    ax2.set_ylim(a,b)

ani = animation.FuncAnimation(fig, animate, interval=10)
plt.show()
conn.close()  # close the connection
