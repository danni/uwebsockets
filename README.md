# Micropython websockets (esp8266 implementation)

An implementation of websockets for the ESP8266 (client only ATM). This is a
work in progress, some of which might move into the modwebsocket C module
that's built into micropython, however that's incomplete, and the handshaking
isn't standard-compliant.

There's no asyncio on the esp8266 (today) but I'd like to build something that
looks for all intents and purposes like a asyncio `Protocol` using the
socket receive handler it does have.

## "Screenshot"

```
$ pip install adafruit-ampy
$ ampy mkdir uwebsockets
$ ampy put uwebsockets/protocol.py uwebsockets/protocol.py
$ ampy put uwebsockets/client.py uwebsockets/client.py
$ ampy run example/client.py
> esp8266 1.5.4(baaeaebb) v1.8.3-80-g1f61fe0-dirty on 2016-08-31 ESP module with ESP8266
< Hello esp8266 1.5.4(baaeaebb) v1.8.3-80-g1f61fe0-dirty on 2016-08-31 ESP module with ESP8266!
```

```
$ pip install websockets
$ python example/server.py
Connection from ('192.168.1.11', 1883)
< esp8266 1.5.4(baaeaebb) v1.8.3-80-g1f61fe0-dirty on 2016-08-31 ESP module with ESP8266
> Hello esp8266 1.5.4(baaeaebb) v1.8.3-80-g1f61fe0-dirty on 2016-08-31 ESP module with ESP8266!
```

## Minimal example client against 'ws://echo.websocket.org/'


```
$ webrepl_client.py 192.168.3.1
Password: 

WebREPL connected
>>> 
>>> 
MicroPython v1.9.4-272-g46091b8a on 2018-07-18; ESP module with ESP8266
Type "help()" for more information.
>>> import echo_websocket_org
The quick brown fox jumps over the lazy dog

>>> 
### closed ###
$ 
$ cat echo_websocket_org.py 
import uwebsockets.client
websocket = uwebsockets.client.connect("ws://echo.websocket.org/")
mesg = "The quick brown fox jumps over the lazy dog"
websocket.send(mesg + "\r\n")
resp = websocket.recv()
print(resp)
assert(mesg + "\r\n" == resp)
$ 
```

# Micropython Socket.io

An implementation of socket.io and engine.io for the ESP8266 (client only ATM).
This is a work in progress and has only been tested against Flask-SocketIO.

There's no asyncio on the esp8266 (today) but I'd like to build something that
looks for all intents and purposes like the socket.io web API. At the moment
this means its own event loop + lots of timeouts.

An interesting example client is
[this OpsGenie bridge](https://github.com/danni/micropython-opsgenie-bridge/tree/master/uclient).

## Compatibility

You might need to bake this code into your firmware to use it. You also need
to bake in the `logging` module. Finally to run the `unix` port you need to
[patch your micropython to support `socket.settimeout`](https://github.com/danni/micropython/tree/2379-unix-settimeout).
