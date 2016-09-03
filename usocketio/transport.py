"""SocketIO transport."""

import logging
import ujson as json
import usocket as socket

import uwebsockets.client
from .protocol import *

LOGGER = logging.getLogger(__name__)


class SocketIO:
    """SocketIO transport."""

    def __init__(self, uri, reconnect=True, **params):
        self.uri = uri
        self.reconnect = reconnect
        self.websocket = uwebsockets.client.connect(uri)

        # Event handlers map from event -> [handlers, ...]
        self._event_handlers = {}
        # Interval handlers [(interval, handler), ...]
        self._interval_handlers = []

        # Register a ping event
        self.at_interval(params['pingInterval'] // 1000)(self.ping)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def close(self):
        self.websocket.close()

    def send(self, message):
        self.emit('message', message)

    def emit(self, event, data):
        self._send_message(MESSAGE_EVENT, (event, data))

    def run_forever(self):
        """Main loop for SocketIO."""
        if __debug__:
            LOGGER.debug("Entering event loop")

        counter = 0

        # send a connection event
        self._handle_event('connection')

        while self.websocket.open or self.reconnect:
            if not self.websocket.open:
                LOGGER.info("Reconnecting")
                self.websocket = uwebsockets.client.connect(self.uri)

            packet_type, data = self._recv()
            self._handle_packet(packet_type, data)
            counter += 1

            for interval, func in self._interval_handlers:
                if counter % interval == 0:
                    func()

        if __debug__:
            LOGGER.debug("Exiting event loop")

    def _handle_packet(self, packet_type, data):
        if packet_type is None:
            pass

        elif packet_type == PACKET_MESSAGE:
            message_type, data = decode_packet(data)
            self._handle_message(message_type, data)

        elif packet_type == PACKET_CLOSE:
            LOGGER.info("Socket.io closed")
            self.close()

        elif packet_type == PACKET_PING:
            LOGGER.debug("< ping")
            self._send_packet(PACKET_PONG, data)

        elif packet_type == PACKET_PONG:
            LOGGER.debug("< pong")

        elif packet_type == PACKET_NOOP:
            pass

        else:
            LOGGER.warning("Unhandled packet %s: %s", packet_type, data)

    def _handle_message(self, message_type, data):
        if message_type == MESSAGE_EVENT:
            event, data = json.loads(data)
            self._handle_event(event, data)

        elif message_type == MESSAGE_ERROR:
            LOGGER.error("Error: %s", data)

        elif message_type == MESSAGE_DISCONNECT:
            LOGGER.info("Disconnected")
            self.close()

        else:
            LOGGER.warning("Unhandled message %s: %s", message_type, data)

    def _handle_event(self, event, data=None):
        if __debug__:
            LOGGER.debug("Handling event '%s'", event)

        for handler in self._event_handlers.get(event, []):
            if __debug__:
                LOGGER.debug("Calling handler %s for event '%s'",
                             handler, event)
            handler(data)

    def _send_packet(self, packet_type, data=''):
        self.websocket.send('{}{}'.format(packet_type, data))

    def _send_message(self, message_type, data=None):
        self._send_packet(PACKET_MESSAGE, '{}{}'.format(message_type,
                                                        json.dumps(data)))

    def ping(self):
        if __debug__:
            LOGGER.debug("> ping")

        self._send_packet(PACKET_PING)

    def _recv(self):
        """Receive a packet."""

        try:
            self.websocket.settimeout(1)
            packet = self.websocket.recv()

            if packet:
                return decode_packet(packet)
            else:
                return None, None

        except OSError:
            return None, None

        finally:
            self.websocket.settimeout(None)

    def on(self, event):
        """Register an event handler with the socket."""

        def inner(func):
            if __debug__:
                LOGGER.debug("Registered %s to handle %s", func, event)

            self._event_handlers.setdefault(event, []).append(func)

        return inner

    def at_interval(self, interval):
        """Register an event handler to happen at an interval."""

        def inner(func):
            if __debug__:
                LOGGER.debug("Registered %s to run at interval %s",
                             func, interval)

            self._interval_handlers.append((interval, func))

        return inner
