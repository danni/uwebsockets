from uaiowebsockets import client
import uasyncio
import sys

async def main():
    async with await client.connect("ws://echo.websocket.org") as websocket:
        await websocket.send("hello, websocket")
        print(await websocket.recv())
        sys.exit(0)

loop = uasyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
