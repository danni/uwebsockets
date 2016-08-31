"""
Websockets client for micropython

Based very heavily off
https://github.com/aaugustin/websockets/blob/master/websockets/client.py
"""

import logging
import urllib.parse
import ubinascii as binascii
import urandom as random
import uasyncio as asyncio

from .protocol import Websocket

LOGGER = logging.getLogger(__name__)


class WebsocketClient(Websocket):
    is_client = True


class connect:
    """
    Connect a websocket.

    This can be used as either a context manager or as a function.
    """

    def __init__(self, uri):
        self.uri = urllib.parse.urlparse(uri)

    async def __iter__(self):
        """This is a hack to allow the websocket = connect() format."""
        return await self._connect()

    async def _connect(self):

        assert self.uri.scheme == 'ws'

        if __debug__: LOGGER.debug("open connection %s:%s",
                                   self.uri.hostname, self.uri.port)

        reader, writer = await asyncio.open_connection(self.uri.hostname,
                                                       self.uri.port)

        async def send_header(header, *args):
            if __debug__: LOGGER.debug(str(header), *args)
            await writer.awrite(header % args + '\r\n')

        # Sec-WebSocket-Key is 16 bytes of random base64 encoded
        key = binascii.b2a_base64(bytes(random.getrandbits(8)
                                        for _ in range(16))).rstrip()

        await send_header(b'GET %s HTTP/1.1', self.uri.path or '/')
        await send_header(b'Host: %s:%s', self.uri.hostname, self.uri.port)
        await send_header(b'Connection: Upgrade')
        await send_header(b'Upgrade: websocket')
        await send_header(b'Sec-WebSocket-Key: %s', key)
        # await send_header(b'Sec-WebSocket-Protocol: chat')
        await send_header(b'Sec-WebSocket-Version: 13')
        await send_header(b'Origin: http://localhost')
        await send_header(b'')

        header = await reader.readline()
        assert header == b'HTTP/1.1 101 Switching Protocols\r\n', header

        # We don't (currently) need these headers
        # FIXME: should we check the return key?
        while header.rstrip():
            if __debug__: LOGGER.debug(str(header))
            header = await reader.readline()

        return WebsocketClient(reader, writer)

    async def __aenter__(self):
        self._websocket = await self._connect()
        return self._websocket

    async def __aexit__(self, exc_type, exc, tb):
        await self._websocket.close()
