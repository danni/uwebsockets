import uwebsockets.client

websocket = uwebsockets.client.connect("ws://echo.websocket.org/")

websocket.send("fo0bAr\r\n")

resp = websocket.recv()

print(resp)
