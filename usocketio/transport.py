"""SocketIO transport."""

from .protocol import decode_packet


class SocketIO:
    """SocketIO transport."""

    def __init__(self, websocket):
        self.websocket = websocket

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def close(self):
        self.websocket.close()

    def wait(self):
        """Main loop for SocketIO."""
        while True:
            packet_type, data = self._recv()
            print(packet_type, data)

    def _send(self, packet_type, data=''):
        self.websocket.send('{}{}'.format(packet_type, data))

    def _recv(self):
        return decode_packet(self.websocket.recv())
