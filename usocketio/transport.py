"""SocketIO transport."""


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
            data = self.websocket.recv()
            print(data)
