import sqlite3
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

DATABASE_FILE = "notes_lab6.db"

app = FastAPI(title="ЛР 6 — FastAPI сервис")


def prepare_database() -> None:
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                details TEXT NOT NULL
            )
            """
        )
        connection.commit()


prepare_database()


class TaskPayload(BaseModel):
    name: str
    details: str


@app.get("/api/status")
def service_status():
    return {
        "service": "lab6-fastapi",
        "variant": 2,
        "features": ["json-response", "sqlite-storage", "websocket-chat"],
    }


@app.post("/tasks")
def add_task(payload: TaskPayload):
    with sqlite3.connect(DATABASE_FILE) as connection:
        cursor = connection.execute(
            "INSERT INTO tasks (name, details) VALUES (?, ?)",
            (payload.name, payload.details),
        )
        connection.commit()
        created_id = cursor.lastrowid
    return {"id": created_id, "name": payload.name, "details": payload.details}


@app.get("/tasks")
def get_tasks():
    with sqlite3.connect(DATABASE_FILE) as connection:
        rows = connection.execute("SELECT id, name, details FROM tasks").fetchall()
    return [{"id": r[0], "name": r[1], "details": r[2]} for r in rows]


WEB_CHAT_PAGE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Чат WebSocket</title>
    <style>
        body { font-family: Segoe UI, Arial, sans-serif; margin: 36px; max-width: 620px; }
        #log { border: 1px solid #bbb; border-radius: 6px; height: 230px; overflow-y: auto; padding: 10px; margin-bottom: 12px; }
        .msg { margin: 4px 0; }
    </style>
</head>
<body>
    <h2>Комната чата (WebSocket)</h2>
    <div id="log"></div>
    <input type="text" id="textBox" placeholder="Сообщение..." autocomplete="off">
    <button id="sendBtn">Отправить</button>

    <script>
        const socket = new WebSocket(`ws://${location.host}/ws/room`);
        const logBox = document.getElementById("log");
        const textBox = document.getElementById("textBox");
        const sendBtn = document.getElementById("sendBtn");

        socket.onmessage = (event) => {
            const line = document.createElement("div");
            line.className = "msg";
            line.textContent = event.data;
            logBox.appendChild(line);
            logBox.scrollTop = logBox.scrollHeight;
        };

        function pushMessage() {
            const val = textBox.value.trim();
            if (!val) return;
            socket.send(val);
            textBox.value = "";
        }

        sendBtn.addEventListener("click", pushMessage);
        textBox.addEventListener("keydown", (e) => {
            if (e.key === "Enter") pushMessage();
        });
    </script>
</body>
</html>
"""


@app.get("/room", response_class=HTMLResponse)
def open_room():
    return WEB_CHAT_PAGE


class SocketHub:
    def __init__(self) -> None:
        self.peers: list[WebSocket] = []

    async def join(self, ws: WebSocket) -> None:
        await ws.accept()
        self.peers.append(ws)

    def leave(self, ws: WebSocket) -> None:
        if ws in self.peers:
            self.peers.remove(ws)

    async def send_all(self, text: str) -> None:
        for peer in list(self.peers):
            await peer.send_text(text)


hub = SocketHub()


@app.websocket("/ws/room")
async def chat_socket(ws: WebSocket):
    await hub.join(ws)
    try:
        while True:
            incoming = await ws.receive_text()
            await hub.send_all(f"[Сообщение]: {incoming}")
    except WebSocketDisconnect:
        hub.leave(ws)