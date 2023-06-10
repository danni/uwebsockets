"""
Websockets client for micropython

Based very heavily off
https://github.com/aaugustin/websockets/blob/master/websockets/client.py
"""

import logging
import usocket as socket
import uasyncio as asyncio
import ubinascii as binascii
import urandom as random
import ussl

from .protocol import Websocket, urlparse

LOGGER = logging.getLogger(__name__)


class WebsocketClient(Websocket):
    is_client = True

async def connect(uri):
    """
    Connect a websocket.
    """

    uri = urlparse(uri)
    assert uri

    if __debug__: LOGGER.debug("open connection %s:%s",
                                uri.hostname, uri.port)

    sock = socket.socket()
    addr = socket.getaddrinfo(uri.hostname, uri.port)
    sock.connect(addr[0][4])
    if uri.protocol == 'wss':
        sock = ussl.wrap_socket(sock)

    sreader = asyncio.StreamReader(sock)
    swriter = asyncio.StreamWriter(sock, {})

    async def send_header(header, *args):
        if __debug__: LOGGER.debug(str(header), *args)
        await swriter.awrite(header % args + '\r\n')

    # Sec-WebSocket-Key is 16 bytes of random base64 encoded
    key = binascii.b2a_base64(bytes(random.getrandbits(8)
                                    for _ in range(16)))[:-1]

    await send_header(b'GET %s HTTP/1.1', uri.path or '/')
    await send_header(b'Host: %s:%s', uri.hostname, uri.port)
    await send_header(b'Connection: Upgrade')
    await send_header(b'Upgrade: websocket')
    await send_header(b'Sec-WebSocket-Key: %s', key)
    await send_header(b'Sec-WebSocket-Version: 13')
    await send_header(b'Origin: http://{hostname}:{port}'.format(
        hostname=uri.hostname,
        port=uri.port)
    )
    await send_header(b'')

    response = await sreader.readline()
    header = response[:-2]
    assert header.startswith(b'HTTP/1.1 101 '), header

    # We don't (currently) need these headers
    # FIXME: should we check the return key?
    while header:
        if __debug__: LOGGER.debug(str(header))
        response = await sreader.readline()
        header = response[:-2]

    return WebsocketClient(sock, sreader, swriter)
