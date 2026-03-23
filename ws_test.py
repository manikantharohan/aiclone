import asyncio
import websockets

async def chat():
    uri = "ws://127.0.0.1:8000/ws/chat/test-session?temperature=0.7&max_tokens=256"
    async with websockets.connect(uri) as ws:
        while True:
            user = input("You: ")
            if not user:
                break
            await ws.send(user)
            reply = ""
            while True:
                chunk = await ws.recv()
                if chunk == "":  # end-of-response marker
                    break
                reply += chunk
            print("Assistant:", reply)

asyncio.run(chat())
