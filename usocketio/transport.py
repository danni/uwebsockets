"""SocketIO transport."""

import logging
import ujson as json
import usocket as socket

from .protocol import *

LOGGER = logging.getLogger(__name__)


class SocketIO:
    """SocketIO transport."""

    def __init__(self, websocket, **params):
        self.websocket = websocket
        self.timeout = params['pingInterval'] // 1000  # seconds
        self._handlers = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def close(self):
        self.websocket.close()

    def run_forever(self):
        """Main loop for SocketIO."""
        LOGGER.debug("Entering event loop")
        while True:
            # FIXME: need a timeout so that we can send ping messages
            packet_type, data = self._recv()
            self._handle_packet(packet_type, data)

    def _handle_packet(self, packet_type, data):
        if packet_type == PACKET_MESSAGE:
            message_type, data = decode_packet(data)
            self._handle_message(message_type, data)
        elif packet_type == PACKET_PONG:
            LOGGER.debug("pong")
        else:
            print("Unhandled packet", packet_type, data)

    def _handle_message(self, message_type, data):
        if message_type == MESSAGE_EVENT:
            event, data = json.loads(data)
            LOGGER.debug("Handling event '%s'", event)

            for handler in self._handlers.get(event, []):
                LOGGER.debug("Calling handler %s for event '%s'",
                             handler, event)
                handler(self, data)
        else:
            print("Unhandled message type", message_type, data)

    def _send_packet(self, packet_type, data=''):
        self.websocket.send('{}{}'.format(packet_type, data))

    def _recv(self):
        """Receive a packet."""

        try:
            LOGGER.debug("Enabling timeouts")
            self.websocket.settimeout(self.timeout)
            return decode_packet(self.websocket.recv())
        except OSError:  # FIXME: socket.timeout ?
            LOGGER.debug("Sending ping")
            self._send_packet(PACKET_PING)
            return decode_packet(self.websocket.recv())
        finally:
            LOGGER.debug("Disabling timeouts")
            self.websocket.settimeout(None)

    def on(self, event):
        """Register an event handler with the socket."""

        def inner(func):
            LOGGER.debug("Registered %s to handle %s", func, event)
            self._handlers.setdefault(event, []).append(func)

        return inner
