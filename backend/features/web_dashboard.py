import asyncio
import logging
import secrets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Header, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional

from backend.config import DASHBOARD_HOST, DASHBOARD_PORT, DASHBOARD_TOKEN

logger = logging.getLogger(__name__)


class CommandRequest(BaseModel):
    """Body model for the command endpoint (validates/limits user input)."""
    command: str


class WebDashboard:
    """Web-based dashboard for SAM monitoring and control"""

    def __init__(self, host: str = None, port: int = None, token: str = None):
        logger.info("🌐 Initializing Web Dashboard...")

        self.host = host or DASHBOARD_HOST
        self.port = port or DASHBOARD_PORT

        # Require a token for all API/WebSocket access. Generate one if not
        # configured so the dashboard is never left completely unauthenticated.
        self.token = token or DASHBOARD_TOKEN or secrets.token_urlsafe(32)
        if not (token or DASHBOARD_TOKEN):
            logger.warning(
                "No DASHBOARD_TOKEN configured; generated a temporary one for "
                "this session: %s", self.token
            )

        self.app = FastAPI(title="SAM Dashboard")
        self.active_connections: List[WebSocket] = []

        self._setup_routes()
        logger.info("✅ Web Dashboard initialized")

    def _require_token(self, x_api_key: Optional[str] = Header(default=None)):
        """Dependency enforcing a valid API key on protected endpoints."""
        if not x_api_key or not secrets.compare_digest(x_api_key, self.token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key",
            )

    def _setup_routes(self):
        """Setup FastAPI routes"""

        @self.app.get("/")
        async def get_dashboard():
            """Serve dashboard HTML"""
            return HTMLResponse(self._get_dashboard_html())

        @self.app.get("/api/status", dependencies=[Depends(self._require_token)])
        async def get_status():
            """Get SAM status"""
            from datetime import datetime
            return {
                'status': 'active',
                'timestamp': datetime.now().isoformat()
            }

        @self.app.get("/api/stats", dependencies=[Depends(self._require_token)])
        async def get_stats():
            """Get system statistics"""
            return {
                'uptime': '24h',
                'interactions': 150,
                'mood': 'happy',
                'api_calls': {'gemini': 45, 'groq': 35}
            }

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket for real-time updates (token required)"""
            token = websocket.query_params.get("token", "")
            if not secrets.compare_digest(token, self.token):
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return

            await websocket.accept()
            self.active_connections.append(websocket)
            try:
                while True:
                    data = await websocket.receive_text()
                    await self.broadcast(f"Message: {data}")
            except WebSocketDisconnect:
                pass
            finally:
                if websocket in self.active_connections:
                    self.active_connections.remove(websocket)

        @self.app.post("/api/command", dependencies=[Depends(self._require_token)])
        async def execute_command(request: CommandRequest):
            """Execute a command"""
            logger.info("💻 Received command request")
            return {'success': True, 'result': f'Command received: {request.command}'}

    async def broadcast(self, message: str):
        """Broadcast message to all connected clients"""
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception:
                if connection in self.active_connections:
                    self.active_connections.remove(connection)

    def _get_dashboard_html(self) -> str:
        """Get dashboard HTML"""
        # The token is injected so the local operator's browser can authenticate.
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SAM Dashboard</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a1a; color: #fff; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                header { text-align: center; padding: 20px 0; border-bottom: 2px solid #00ff00; margin-bottom: 30px; }
                h1 { font-size: 2.5em; color: #00ff00; }
                .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
                .stat-card { background: #2a2a2a; padding: 20px; border-radius: 10px; border-left: 4px solid #00ff00; }
                .stat-card h3 { margin-bottom: 10px; }
                .stat-card .value { font-size: 2em; color: #00ff00; font-weight: bold; }
                .command-box { background: #2a2a2a; padding: 20px; border-radius: 10px; margin-top: 20px; }
                input { width: 100%; padding: 10px; background: #1a1a1a; border: 1px solid #00ff00; color: #fff; border-radius: 5px; }
                button { background: #00ff00; color: #000; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; margin-top: 10px; }
                button:hover { background: #00dd00; }
                .log-area { background: #2a2a2a; padding: 15px; border-radius: 10px; margin-top: 20px; height: 200px; overflow-y: auto; font-family: monospace; font-size: 0.9em; }
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>🤖 SAM Dashboard</h1>
                    <p>Agentic AI Assistant Control Panel</p>
                </header>

                <div class="stats">
                    <div class="stat-card">
                        <h3>Status</h3>
                        <div class="value" id="status">Active</div>
                    </div>
                    <div class="stat-card">
                        <h3>Interactions</h3>
                        <div class="value" id="interactions">0</div>
                    </div>
                    <div class="stat-card">
                        <h3>Mood</h3>
                        <div class="value" id="mood">Neutral</div>
                    </div>
                    <div class="stat-card">
                        <h3>API Calls</h3>
                        <div class="value" id="api_calls">0</div>
                    </div>
                </div>

                <div class="command-box">
                    <h3>💻 Send Command</h3>
                    <input type="text" id="command_input" placeholder="Enter command...">
                    <button onclick="sendCommand()">Execute</button>
                </div>

                <div class="log-area" id="log_area"></div>
            </div>

            <script>
                const API_TOKEN = "__DASHBOARD_TOKEN__";

                // Connect to WebSocket
                const ws = new WebSocket(`ws://${location.host}/ws?token=${encodeURIComponent(API_TOKEN)}`);

                ws.onmessage = (event) => {
                    const logArea = document.getElementById('log_area');
                    // Use textContent to avoid HTML/script injection (XSS).
                    const line = document.createElement('div');
                    line.textContent = event.data;
                    logArea.appendChild(line);
                    logArea.scrollTop = logArea.scrollHeight;
                };

                async function sendCommand() {
                    const input = document.getElementById('command_input');
                    const command = input.value;

                    await fetch('/api/command', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-API-Key': API_TOKEN
                        },
                        body: JSON.stringify({command})
                    });

                    input.value = '';
                }

                // Update stats
                async function updateStats() {
                    const response = await fetch('/api/stats', {
                        headers: {'X-API-Key': API_TOKEN}
                    });
                    if (!response.ok) return;
                    const data = await response.json();
                    document.getElementById('interactions').textContent = data.interactions;
                    document.getElementById('mood').textContent = data.mood;
                }

                setInterval(updateStats, 3000);
            </script>
        </body>
        </html>
        """.replace("__DASHBOARD_TOKEN__", self.token)

    async def run(self):
        """Run the dashboard server"""
        import uvicorn
        logger.info(f"🌐 Dashboard running at http://{self.host}:{self.port}")
        await asyncio.to_thread(
            uvicorn.run,
            self.app,
            host=self.host,
            port=self.port
        )


if __name__ == "__main__":
    dashboard = WebDashboard()
