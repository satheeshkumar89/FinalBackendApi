import socketio
import time
import requests
import threading

# Use local server for testing
URL = "http://127.0.0.1:8000"

def start_server():
    import subprocess
    return subprocess.Popen(["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"])

def run_test():
    # Initialize client with ONLY polling transport
    sio = socketio.Client(logger=True, engineio_logger=True)
    
    events_received = []

    @sio.on('connect')
    def on_connect():
        print("Connected via polling!")
        sio.emit('request_join', {'room': 'test_room'})

    @sio.on('room_joined')
    def on_join(data):
        print(f"Joined room: {data}")
        # Trigger a mock event via a separate thread or just wait
        events_received.append('joined')

    @sio.on('order_update')
    def on_order_update(data):
        print(f"Received order update: {data}")
        events_received.append('update')

    try:
        # Connect using default transports (polling then upgrade to websocket)
        sio.connect(URL, socketio_path='socket.io')
        
        # Wait for join confirmation
        time.sleep(2)
        
        if 'joined' in events_received:
            print("✅ Handshake and Room Join successful!")
        else:
            print("❌ Room Join failed.")

        # Manually trigger an event from the server side if possible, 
        # or just confirm connectivity is enough.
        
        sio.disconnect()
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    server_proc = start_server()
    time.sleep(5) # Wait for server to start
    
    try:
        run_test()
    finally:
        server_proc.terminate()
        print("Server stopped.")
