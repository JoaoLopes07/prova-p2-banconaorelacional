from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from aioredis import Redis, create_redis_pool
import uvicorn
import os

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
        self.next_client_id = 1  # Inicializa o contador de clientes

    async def connect(self, websocket: WebSocket):
        client_id = self.next_client_id
        self.next_client_id += 1  # Incrementa o contador de clientes para o próximo
        await websocket.accept()
        self.active_connections[client_id] = websocket
        await self.broadcast(f"Cliente {client_id} entrou no chat.")  # Envia mensagem de boas-vindas

    def disconnect(self, client_id: int):
        del self.active_connections[client_id]

    async def send_personal_message(self, message: str, client_id: int):
        websocket = self.active_connections.get(client_id)
        if websocket:
            await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

class ChatStorage:
    def __init__(self):
        self.redis = None

    async def connect_redis(self):
        self.redis = await create_redis_pool("redis://localhost")

    async def close_redis(self):
        self.redis.close()
        await self.redis.wait_closed()

    async def save_message(self, client_id: int, message: str):
        await self.redis.lpush(f"chat:{client_id}", message)

    async def get_messages(self, client_id: int):
        messages = await self.redis.lrange(f"chat:{client_id}", 0, -1)
        return [message.decode() for message in messages]

manager = ConnectionManager()
storage = ChatStorage()
html_file = os.path.join("templates", "index.html")

@app.on_event("startup")
async def startup_event():
    await storage.connect_redis()

@app.on_event("shutdown")
async def shutdown_event():
    await storage.close_redis()

@app.get("/", response_class=HTMLResponse)
async def get():
    with open(html_file, "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    client_id = manager.next_client_id - 1  # O ID do cliente é o ID atual menos 1
    try:
        old_messages = await storage.get_messages(client_id)
        for message in old_messages:
            await manager.send_personal_message(message, client_id)

        while True:
            data = await websocket.receive_text()
            await storage.save_message(client_id, f"Cliente {client_id} disse: {data}")
            await manager.broadcast(f"Cliente {client_id} disse: {data}")

    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast(f"Cliente {client_id} saiu do chat")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

