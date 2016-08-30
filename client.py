"""
Websockets client for micropython

Based very heavily off
https://github.com/aaugustin/websockets/blob/master/websockets/client.py
"""

import logging
import urllib.parse
import base64
import urandom as random
import uasyncio as asyncio

from .protocol import Websocket

LOGGER = logging.getLogger(__name__)


class WebsocketClient(Websocket):
    is_client = True


async def connect(uri):
    """Connect a websocket."""

    uri = urllib.parse.urlparse(uri)

    assert uri.scheme == 'ws'

    if __debug__: LOGGER.debug("open connection %s:%s", uri.hostname, uri.port)

    reader, writer = await asyncio.open_connection(uri.hostname, uri.port)

    async def send_header(header, *args):
        if __debug__: LOGGER.debug(header, *args)
        await writer.awrite(header % args + '\r\n')

    # Sec-WebSocket-Key is 16 bytes of random base64 encoded
    key = base64.b64encode(bytes(random.getrandbits(8) for _ in range(16)))

    await send_header(b'GET %s HTTP/1.1', uri.path)
    await send_header(b'Host: %s:%s', uri.hostname, uri.port)
    await send_header(b'Connection: Upgrade')
    await send_header(b'Upgrade: websocket')
    await send_header(b'Sec-WebSocket-Key: %s', key)
    # await send_header(b'Sec-WebSocket-Protocol: chat')
    await send_header(b'Sec-WebSocket-Version: 13')
    await send_header(b'Origin: http://localhost')
    await send_header(b'')

    header = await reader.readline()
    assert header == b'HTTP/1.1 101 Switching Protocols\r\n'

    # We don't (currently) need these headers
    # FIXME: should we check the return key?
    while header.strip():
        if __debug__: LOGGER.debug(header)
        header = await reader.readline()

    return WebsocketClient(reader, writer)
