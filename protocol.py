"""
Websockets protocol
"""

import struct

# Opcodes
OP_CONT = 0x0
OP_TEXT = 0x1
OP_BYTES = 0x2
OP_CLOSE = 0x8
OP_PING = 0x9
OP_PONG = 0xa


class Websocket:
    is_masked = is_server = is_client = False

    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer

    async def write_frame(self, opcode, data=b''):
        """
        Write a frame to the socket.
        See https://tools.ietf.org/html/rfc6455#section-5.2 for the details.
        """
        fin = True
        mask = self.is_masked

        length = len(data)

        #
        # Frame header
        # Byte 1: FIN(1) _(1) _(1) _(1) OPCODE(4)
        byte1 = 1 << 7 if fin else 0
        byte1 |= opcode

        # Byte 2: MASK(1) LENGTH(7)
        byte2 = 1 << 7 if mask else 0

        if length < 126:  # 126 is magic value to use 2-byte length header
            byte2 |= length
            await self.writer.awrite(struct.pack('!BB',
                                                 byte1, byte2))

        elif length < (1 << 16):  # Length fits in 2-bytes
            byte2 |= 126  # Magic code
            await self.writer.awrite(struct.pack('!BBH',
                                                 byte1, byte2, length))

        elif length < (1 << 64):
            byte2 |= 127  # Magic code
            await self.writer.awrite(struct.pack('!BBQ',
                                                 byte1, byte2, length))

        else:
            raise ValueError()

        if mask:
            mask_bits = struct.pack('!I', 0xaaaa)  # FIXME: no RNG available
            await self.writer.awrite(mask_bits)

            data = bytes(b ^ mask_bits[i % 4]
                         for i, b in enumerate(data))

        await self.writer.awrite(data)

    async def recv(self):
        return await self.reader.read()

    async def send(self, buf):
        if isinstance(buf, str):
            opcode = OP_TEXT
            buf = buf.encode('utf-8')
        elif isinstance(buf, bytes):
            opcode = OP_BYTES
        else:
            raise TypeError()

        return await self.write_frame(opcode, buf)
