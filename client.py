import asyncio
import websockets

async def test_chat():
    uri = "ws://127.0.0.1:8000/ws/chat/1/"  # ✅ adjust thread_id if needed
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket server!")

        # Send a test message
        await websocket.send("Hello from client!")
        print("Sent: Hello from client!")

        # Wait for response
        response = await websocket.recv()
        print(f"Received: {response}")

asyncio.run(test_chat())
