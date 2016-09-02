import logging

import usocketio.client

logging.basicConfig(level=logging.DEBUG)

def hello():
    with usocketio.client.connect('http://127.0.0.1:5000/') as socketio:
        @socketio.on('message')
        def on_message(self, message):
            print("message", message)

        @socketio.on('alert')
        def on_alert(self, message):
            print("alert", message)

        socketio.run_forever()

hello()
