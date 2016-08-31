import uasyncio as asyncio
import uwebsockets.client

async def hello():
    async with uwebsockets.client.connect('ws://127.0.0.1:5000') as websocket:

        name = "Badger"
        await websocket.send(name)
        print("> {}".format(name))

        greeting = await websocket.recv()
        print("< {}".format(greeting))

asyncio.get_event_loop().run_until_complete(hello())
