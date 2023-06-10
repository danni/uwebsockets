from uaiowebsockets import client
import uasyncio


async def connect_and_receive(loop):
    websocket = await client.connect("ws://echo.websocket.org")

    loop.create_task(writer(1, websocket))
    loop.create_task(writer(2, websocket))

    while True:
        print(await websocket.recv())


async def writer(index, websocket):
    message_num = 0
    while True:
        message_num += 1
        msg = "[%s]: Hello from writer %s." % (message_num, index)
        await websocket.send(msg)
        await uasyncio.sleep(5)


loop = uasyncio.get_event_loop()
loop.create_task(connect_and_receive(loop))
loop.run_forever()
