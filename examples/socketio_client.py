import logging

import usocketio.client

logging.basicConfig(level=logging.DEBUG)

def hello():
    with usocketio.client.connect('http://127.0.0.1:5000/') as socketio:
        print(socketio)
        socketio.wait()

hello()
