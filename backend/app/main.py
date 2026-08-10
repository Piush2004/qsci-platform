import sys
import os
import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Insert root project path so imports work
sys.path.insert(0, 'd:/Projects/QML project')

from backend.app.api.routes import api_router
from backend.app.db.database import init_db
from backend.app.config import settings
from backend.app.core.errors import register_error_handlers
from backend.app.core.events import event_bus

import random

# WebSocket clients
connected_clients = set()

async def broadcast_kpis():
    while True:
        if connected_clients:
            kpi_data = {
                "forecast_confidence": round(random.uniform(0.85, 0.90), 2),
                "expected_savings": 125000.0 + random.randint(-1000, 1000),
                "risk_level": "Medium",
                "pending_approvals_count": random.randint(1, 5)
            }
            message = json.dumps(kpi_data)
            dead_clients = set()
            for client in connected_clients:
                try:
                    await client.send_text(message)
                except Exception:
                    dead_clients.add(client)
            connected_clients.difference_update(dead_clients)
        await asyncio.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Init DB and Event Bus
    await init_db()
    await event_bus.connect()
    # Start WebSocket broadcaster
    asyncio.create_task(broadcast_kpis())
    yield
    # Shutdown

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Register RFC 7807 error handlers
register_error_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
