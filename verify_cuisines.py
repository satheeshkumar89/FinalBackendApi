from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

response = client.get("/restaurant/cuisines/available")
if response.status_code == 200:
    data = response.json()["data"]["cuisines"]
    print(f"Total cuisines: {len(data)}")
    print("First 10 cuisines:")
    for c in data[:10]:
        print(f"ID: {c['id']}, Name: {c['name']}")
else:
    print(f"Failed: {response.status_code}")
