"""
Websockets client for micropython

Based very heavily off
https://github.com/aaugustin/websockets/blob/master/websockets/client.py
"""

import logging
import urllib.parse

import uasyncio as asyncio

from .protocol import Websocket

# logging.basicConfig(logging.DEBUG)


class WebsocketClient(Websocket):
    is_masked = is_client = True


async def connect(uri, *, loop=None):
    """Connect a websocket."""

    if loop is None:
        loop = asyncio.get_event_loop()

    uri = urllib.parse.urlparse(uri)

    assert uri.scheme == 'ws'

    print("open connection", uri.hostname, uri.port)
    reader, writer = await asyncio.open_connection(uri.hostname, uri.port)
    print(reader, writer)

    async def send_header(header, *args):
        print(header % args)
        await writer.awrite(header % args + '\r\n')

    await send_header(b'GET %s HTTP/1.1', uri.path)
    await send_header(b'Host: %s:%s', uri.hostname, uri.port)
    await send_header(b'Connection: Upgrade')
    await send_header(b'Upgrade: websocket')
    # FIXME: generate a useful key
    await send_header(b'Sec-WebSocket-Key: %s', 'x3JJHMbDL1EzLkh9GBhXDw==')
    # await send_header(b'Sec-WebSocket-Protocol: chat')
    await send_header(b'Sec-WebSocket-Version: 13')
    await send_header(b'Origin: http://localhost')
    await send_header(b'')

    print("Awaiting response")

    header = await reader.readline()
    assert header == b'HTTP/1.1 101 Switching Protocols\r\n'

    # We don't (currently) need these headers
    while header.strip():
        print(header)
        header = await reader.readline()

    print("!")

    return WebsocketClient(reader, writer)
