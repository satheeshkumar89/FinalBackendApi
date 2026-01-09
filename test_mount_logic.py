
import socketio
from fastapi import FastAPI
import uvicorn
from starlette.testclient import TestClient

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
sio_app = socketio.ASGIApp(sio, socketio_path='')

app = FastAPI()
app.mount("/socket.io", sio_app)

@app.get("/")
def read_root():
    return {"status": "ok"}

if __name__ == "__main__":
    # Just to verify it starts up without errors
    print("FastAPI with Socket.IO mount initialized")
