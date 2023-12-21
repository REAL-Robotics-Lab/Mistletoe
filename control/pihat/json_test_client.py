"""
credit: https://codereview.stackexchange.com/questions/269519/json-packet-transmitter
"""

import socket
import json
from random import randint,randrange
import time
from typing import Dict, Any


IP = "192.168.1.129"
PORT = 5000

def generate_json_message() -> Dict[str, Any]:
    # """Generate random json packet with hashed data bits"""
    return {
            "main": {
                "timestamp": time.time(),
            },
            "motor_11": {
                "Position": str(randrange(-10,10)),
                "Desired Position": str(randrange(-10,10))
            }
        }


def send_json_message(
    sock: socket.socket,
    json_message: Dict[str, Any],
) -> None:
    """Send json packet to server"""
    message = (json.dumps(json_message) + '\n').encode()
    sock.sendall(message)
    print(f'{len(message)} bytes sent')


def main() -> None:
    with socket.socket() as sock:
        sock.connect((IP, PORT))
        while True:
            json_message = generate_json_message()
            send_json_message(sock, json_message)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
