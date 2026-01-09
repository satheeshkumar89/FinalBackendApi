import requests
import websocket
import ssl

def check_socketio_polling(url):
    print(f"Checking polling: {url}/socket.io/?EIO=4&transport=polling")
    try:
        resp = requests.get(f"{url}/socket.io/?EIO=4&transport=polling")
        print(f"Polling Status: {resp.status_code}")
        print(f"Polling Response: {resp.text}")
    except Exception as e:
        print(f"Polling Error: {e}")

def check_websocket_upgrade(url):
    # Convert https to wss
    ws_url = url.replace("https://", "wss://").replace("http://", "ws://")
    full_ws_url = f"{ws_url}/socket.io/?EIO=4&transport=websocket"
    print(f"Checking WebSocket Upgrade: {full_ws_url}")
    
    try:
        ws = websocket.create_connection(full_ws_url, sslopt={"cert_reqs": ssl.CERT_NONE})
        print("WebSocket Upgrade Successful!")
        ws.close()
    except Exception as e:
        print(f"WebSocket Upgrade Failed: {e}")

if __name__ == "__main__":
    target_url = "https://dharaifooddelivery.in"
    check_socketio_polling(target_url)
    print("-" * 20)
    check_websocket_upgrade(target_url)
