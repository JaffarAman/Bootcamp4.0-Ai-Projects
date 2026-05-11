from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.admin_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket, role: str = "admin"):
        await websocket.accept()
        self.active_connections.append(websocket)
        if role == "admin":
            self.admin_connections.append(websocket)
        print(f"✅ Connected | Role: {role} | Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections = [c for c in self.active_connections if c != websocket]
        self.admin_connections = [c for c in self.admin_connections if c != websocket]

    async def notify_admins(self, message: str):
        dead = []
        for conn in self.admin_connections:
            try:
                await conn.send_json({"message": message})
                print(f"📨 WS Notification sent: {message}")
            except Exception as e:
                dead.append(conn)
        for conn in dead:
            self.disconnect(conn)


manager = ConnectionManager()
