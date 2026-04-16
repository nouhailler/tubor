"""
Tubor Web — Gestionnaire de connexions WebSocket
Permet de broadcaster les événements depuis les threads vers les clients WebSocket.
"""

import asyncio
from fastapi import WebSocket


class ConnectionManager:
    """Gère les connexions WebSocket actives et le broadcast thread-safe."""

    def __init__(self):
        self._connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        async with self._lock:
            self._connections.add(ws)

    async def disconnect(self, ws: WebSocket):
        async with self._lock:
            self._connections.discard(ws)

    async def broadcast(self, data: dict):
        dead: set[WebSocket] = set()
        async with self._lock:
            conns = set(self._connections)

        for ws in conns:
            try:
                await ws.send_json(data)
            except Exception:
                dead.add(ws)

        if dead:
            async with self._lock:
                self._connections -= dead


manager = ConnectionManager()
