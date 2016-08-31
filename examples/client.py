import uwebsockets.client

def hello():
    with uwebsockets.client.connect('ws://127.0.0.1:5000') as websocket:

        name = "Badger"
        websocket.send(name)
        print("> {}".format(name))

        greeting = websocket.recv()
        print("< {}".format(greeting))

hello()
