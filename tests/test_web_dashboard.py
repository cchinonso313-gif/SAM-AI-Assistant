import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from backend.features.web_dashboard import WebDashboard


class TestWebDashboard:
    """Test suite for the Web Dashboard"""

    @pytest.fixture
    def dashboard(self):
        return WebDashboard(host="127.0.0.1", port=8123)

    @pytest.fixture
    def client(self, dashboard):
        return TestClient(dashboard.app)

    def test_initialization(self, dashboard):
        """Dashboard should configure host, port and app"""
        assert dashboard.host == "127.0.0.1"
        assert dashboard.port == 8123
        assert dashboard.app is not None
        assert dashboard.active_connections == []

    def test_root_serves_html(self, client):
        """The root route should serve the dashboard HTML"""
        response = client.get("/")
        assert response.status_code == 200
        assert "SAM Dashboard" in response.text

    def test_status_endpoint(self, client):
        """The status endpoint should report an active status"""
        response = client.get("/api/status")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "active"
        assert "timestamp" in body

    def test_stats_endpoint(self, client):
        """The stats endpoint should return usage statistics"""
        response = client.get("/api/stats")
        assert response.status_code == 200
        body = response.json()
        assert body["interactions"] == 150
        assert body["api_calls"] == {"gemini": 45, "groq": 35}

    def test_command_endpoint(self, client):
        """The command endpoint should echo the executed command"""
        response = client.post("/api/command", params={"command": "ping"})
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "ping" in body["result"]

    def test_dashboard_html_content(self, dashboard):
        """The dashboard HTML should include core UI markers"""
        html = dashboard._get_dashboard_html()
        assert "<!DOCTYPE html>" in html
        assert "SAM Dashboard" in html
        assert "sendCommand" in html

    @pytest.mark.asyncio
    async def test_broadcast_sends_to_all_connections(self, dashboard):
        """Broadcast should push messages to every active connection"""
        conn_a = AsyncMock()
        conn_b = AsyncMock()
        dashboard.active_connections = [conn_a, conn_b]

        await dashboard.broadcast("hello")

        conn_a.send_text.assert_awaited_once_with("hello")
        conn_b.send_text.assert_awaited_once_with("hello")

    @pytest.mark.asyncio
    async def test_broadcast_ignores_failing_connection(self, dashboard):
        """A failing connection should not break the broadcast loop"""
        good = AsyncMock()
        bad = AsyncMock()
        bad.send_text.side_effect = RuntimeError("closed")
        dashboard.active_connections = [bad, good]

        await dashboard.broadcast("ping")

        good.send_text.assert_awaited_once_with("ping")

    def test_websocket_endpoint(self, client, dashboard):
        """The websocket endpoint should echo broadcast messages"""
        with client.websocket_connect("/ws") as ws:
            ws.send_text("hi")
            assert ws.receive_text() == "Message: hi"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
