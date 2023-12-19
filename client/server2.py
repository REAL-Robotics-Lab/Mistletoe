import socket

class WSServer():
    def __init__(self) -> None:
        pass

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
y = []    

counter = 0

def animate(i):

    global counter

    # receive data stream. it won't accept data packet greater than 1024 bytes
    data = conn.recv(1024).decode()
    if not data:
        # if data is not received break
        return
    print("from connected user: " + str(data))
    conn.send('b'.encode())  # send data to the client

    counter += 1
    
    x.append(counter)
    y.append(data)
    ax1.clear()
    ax1.plot(x, y)

ani = animation.FuncAnimation(fig, animate, interval=10)
plt.show()
conn.close()  # close the connection
