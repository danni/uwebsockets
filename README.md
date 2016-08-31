# Micropython websockets (esp8266 implementation)

An implementation of websockets for the ESP8266 (client only ATM). This is a
work in progress, some of which might move into the modwebsocket C module
that's built into micropython, however that's incomplete, and the handshaking
isn't standard-compliant.

There's no asyncio on the esp8266 (today) but I'd like to build something that
looks for all intents and purposes like a asyncio `Protocol` using the
socket receive handler it does have.

Currently requires you to freeze the `logging` module into your firmware,
however that could be stubbed out.

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
