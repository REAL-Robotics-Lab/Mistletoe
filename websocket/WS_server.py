import socket
import pickle
import json

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

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

x = [0 for i in range(10)]
y_1 = [0 for i in range(10)]
y_2 = [0 for i in range(10)]

max_len = 10

def animate(i):

    # receive data stream. it won't accept data packet greater than 1024 bytes
    data = conn.recv(1024)

    if not data:
        # if data is not received break
        return

    print(len(data))
    data = pickle.loads(data)
    

    # print(data)

    # print("from connected user: " + str(data))
    conn.send('b'.encode())  # send data to the client

    counter = float(data["main"]["timestamp"])
    real_pos = float(data["motor_11"]["Position"])
    desired_pos = float(data["motor_11"]["Desired Position"])

    x.append(counter)
    y_1.append(desired_pos)
    y_2.append(real_pos)

    ax1.clear()
    ax1.plot(x[-10::1], y_1[-10::1], color='red')
    ax2 = ax1.twinx()
    ax2.plot(x[-10::1], y_2[-10::1], color='blue')

    a,b = -1,1
    ax1.set_ylim(a,b)
    ax2.set_ylim(a,b)

ani = animation.FuncAnimation(fig, animate, interval=10)
plt.show()
conn.close()  # close the connection
