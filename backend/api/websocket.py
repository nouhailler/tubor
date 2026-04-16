"""
Tubor Web — Endpoint WebSocket /ws
Envoie un snapshot initial (état + ordre de la file) puis broadcaste tous les événements.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from api.broadcast import manager
from core.downloader import download_manager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        await ws.send_json({
            "type":        "snapshot",
            "downloads":   download_manager.get_all(),
            "queue_order": download_manager.get_queue_order(),
        })

        while True:
            await ws.receive_text()

    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(ws)
