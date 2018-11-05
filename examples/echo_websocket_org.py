import uwebsockets.client
websocket = uwebsockets.client.connect("ws://echo.websocket.org/")
mesg = "The quick brown fox jumps over the lazy dog"
websocket.send(mesg + "\r\n")
resp = websocket.recv()
print(resp)
assert(mesg + "\r\n" == resp)
# close the socket to reclaim memory
websocket.close()
