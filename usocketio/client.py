"""
Micropython Socket.IO client.
"""

import logging
import ure as re
import ujson as json
import usocket as socket
from ucollections import namedtuple

import uwebsockets.client

from .protocol import decode_payload, PACKET_OPEN
from .transport import SocketIO

LOGGER = logging.getLogger(__name__)

URL_RE = re.compile(r'http://([A-Za-z0-9\-\.]+)(?:\:([0-9]+))?(/.+)?')
URI = namedtuple('URI', ('hostname', 'port', 'path'))


def urlparse(uri):
    """Parse http:// URLs"""
    match = URL_RE.match(uri)
    if match:
        return URI(match.group(1), int(match.group(2)), match.group(3))


def _connect_http(hostname, port, path):
    """Stage 1 do the HTTP connection to get our SID"""
    try:
        sock = socket.socket()
        addr = socket.getaddrinfo(hostname, port)
        sock.connect(addr[0][4])

        def send_header(header, *args):
            if __debug__:
                LOGGER.debug(str(header), *args)

            sock.send(header % args + '\r\n')

        send_header(b'GET %s HTTP/1.1', path)
        send_header(b'Host: %s:%s', hostname, port)
        send_header(b'')

        header = sock.readline()[:-2]
        assert header == b'HTTP/1.1 200 OK', header

        length = None

        # We don't (currently) need these headers
        while header:
            if __debug__:
                LOGGER.debug(str(header))

            header = sock.readline()[:-2]
            if not header:
                break

            header, value = header.split(b': ')
            header = header.lower()
            if header == b'content-type':
                assert value == b'application/octet-stream'
            elif header == b'content-length':
                length = int(value)

        assert length

        data = sock.read(length)
        packet_type, data = next(decode_payload(data))

        assert packet_type == PACKET_OPEN
        return json.loads(data)

    finally:
        sock.close()


def connect(uri):
    """Connect to a socket IO server."""
    uri = urlparse(uri)

    assert uri

    path = uri.path or '/' + 'socket.io/?EIO=3'

    params = _connect_http(uri.hostname, uri.port, path)

    assert 'websocket' in params['upgrades']

    sid = params['sid']
    path += '&sid={}'.format(sid)

    if __debug__:
        LOGGER.debug("Connecting to websocket SID %s", sid)

    websocket = uwebsockets.client.connect(
        'ws://{hostname}:{port}{path}'.format(
            hostname=uri.hostname,
            port=uri.port,
            path=path))

    return SocketIO(websocket)
