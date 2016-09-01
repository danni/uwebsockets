"""
Micropython Socket.IO client.
"""

import logging
import ure as re
import usocket as socket
from ucollections import namedtuple

from .protocol import decode_payload

LOGGER = logging.getLogger(__name__)

URL_RE = re.compile(r'http://([A-Za-z0-9\-\.]+)(?:\:([0-9]+))?(/.+)?')
URI = namedtuple('URI', ('hostname', 'port', 'path'))


def urlparse(uri):
    """Parse ws:// URLs"""
    match = URL_RE.match(uri)
    if match:
        return URI(match.group(1), int(match.group(2)), match.group(3))


def connect(uri):
    """Connect to a socket IO server."""
    uri = urlparse(uri)

    assert uri

    try:
        sock = socket.socket()
        addr = socket.getaddrinfo(uri.hostname, uri.port)
        sock.connect(addr[0][4])

        def send_header(header, *args):
            if __debug__: LOGGER.debug(str(header), *args)
            sock.send(header % args + '\r\n')

        path = uri.path or '/' + 'socket.io/?EIO=3'

        send_header(b'GET %s HTTP/1.1', path)
        send_header(b'Host: %s:%s', uri.hostname, uri.port)
        send_header(b'')

        header = sock.readline()[:-2]
        assert header == b'HTTP/1.1 200 OK', header

        length = None

        # We don't (currently) need these headers
        while header:
            if __debug__: LOGGER.debug(str(header))
            header = sock.readline()[:-2]
            if not header:
                break

            header, value = header.split(b': ')
            header = header.lower()
            print(header, value)
            if header == b'content-type':
                assert value == b'application/octet-stream'
            elif header == b'content-length':
                length = int(value)

        assert length

        buf = sock.read(length)
        for packet in decode_payload(buf):
            print(packet)

    finally:
        sock.close()
