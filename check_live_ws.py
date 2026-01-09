import requests
import websocket
import ssl
import socket

def check_socketio_polling(url):
    print(f"Checking polling: {url}/socket.io/?EIO=4&transport=polling")
    try:
        resp = requests.get(f"{url}/socket.io/?EIO=4&transport=polling", timeout=10)
        print(f"Polling Status: {resp.status_code}")
        print(f"Polling Response: {resp.text}")
        return resp.status_code == 200
    except Exception as e:
        print(f"Polling Error: {e}")
        return False

def check_websocket_upgrade(url):
    # Convert https to wss
    ws_url = url.replace("https://", "wss://").replace("http://", "ws://")
    full_ws_url = f"{ws_url}/socket.io/?EIO=4&transport=websocket"
    print(f"\nChecking WebSocket Upgrade via Nginx: {full_ws_url}")
    
    try:
        ws = websocket.create_connection(full_ws_url, sslopt={"cert_reqs": ssl.CERT_NONE}, timeout=10)
        print("✅ WebSocket Upgrade Successful via Nginx!")
        ws.close()
    except Exception as e:
        print(f"❌ WebSocket Upgrade Failed via Nginx: {e}")
        print("Suggestion: Check Nginx configuration for Upgrade and Connection headers.")

def check_direct_port(ip, port):
    url = f"ws://{ip}:{port}/socket.io/?EIO=4&transport=websocket"
    print(f"\nChecking Direct WebSocket Connection: {url}")
    try:
        ws = websocket.create_connection(url, timeout=10)
        print(f"✅ WebSocket Direct Connection Successful on port {port}!")
        ws.close()
    except Exception as e:
        print(f"❌ WebSocket Direct Connection Failed on port {port}: {e}")

if __name__ == "__main__":
    target_url = "https://dharaifooddelivery.in"
    server_ip = "52.22.224.42"
    
    print("=== Socket.IO Diagnostics ===")
    check_socketio_polling(target_url)
    print("-" * 30)
    check_websocket_upgrade(target_url)
    print("-" * 30)
    check_direct_port(server_ip, 8000)
    print("=============================")
