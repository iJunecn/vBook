"""最小烟雾测试：在不连外部 API 的情况下验证应用启动"""
import os
os.environ["AGNES_API_KEY"] = ""
os.environ["PADDLE_OCR_TOKEN"] = ""

from fastapi.testclient import TestClient
from app.main import app


def test_health_and_root():
    c = TestClient(app)
    assert c.get("/health").json()["status"] == "ok"
    assert c.get("/").json()["app"] == "贝壳易书"


def test_register_login_flow():
    c = TestClient(app)
    r = c.post("/api/v1/auth/register", json={
        "username": "tester01", "email": "t@example.com", "password": "secret123"
    })
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}
    me = c.get("/api/v1/auth/me", headers=h).json()
    assert me["username"] == "tester01"


def test_listings_empty():
    c = TestClient(app)
    r = c.get("/api/v1/listings")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
