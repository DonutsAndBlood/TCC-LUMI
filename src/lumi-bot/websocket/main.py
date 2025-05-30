import socketio  # type: ignore[import-untyped]
from aiohttp import web

sio = socketio.AsyncServer(
    async_mode="aiohttp",
    cors_allowed_origins=[
        "http://localhost:*",
        "https://admin.socket.io",
        "https://piehost.com",
    ],
)
sio.instrument(auth={"username": "admin", "password": "admin123lumi"})
clients: set[str] = set()


@sio.event
async def connect(sid, environ, auth=None):
    print("connect ", sid)
    clients.add(sid)
    print(f"current clients: {', '.join(clients)}")


@sio.event
async def msg(sid, text):
    print(f"received: {text}")


@sio.event
async def disconnect(sid, reason):
    if reason == sio.reason.CLIENT_DISCONNECT:
        print("the client disconnected")
    elif reason == sio.reason.SERVER_DISCONNECT:
        print("the server disconnected the client")
    else:
        print("disconnect reason:", reason)
    clients.remove(sid)


async def send_transcript(text: str):
    return sio.emit("transcript", text)


def start_websocket():
    app = web.Application()
    sio.attach(app)
    web.run_app(app, port=25565)


# sio.emit("transcript", {"data": "foobar"})

if __name__ == "__main__":
    start_websocket()
    print("Starting echo server...")
