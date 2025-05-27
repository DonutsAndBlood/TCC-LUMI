#!/usr/bin/env python

"""Echo server using the asyncio API."""

import asyncio
from websockets.asyncio.server import serve


async def handler(websocket):
    async for message in websocket:
        await websocket.send(message)


async def main():
    print("Starting handler server on ws://localhost:8765")
    async with serve(handler, "localhost", 8765) as server:
        await server.serve_forever()


if __name__ == "__main__":
    print("Starting echo server...")
    asyncio.run(main=main())
