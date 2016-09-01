import usocketio.client

def hello():
    socket = usocketio.client.connect('http://127.0.0.1:5000/')

hello()
