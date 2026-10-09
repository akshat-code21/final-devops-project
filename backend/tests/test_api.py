import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    # Keep database tables for inspection or teardown if needed

def test_health_check():
    """Verify health endpoint returns UP status for Kubernetes liveness probe."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}

def test_root_endpoint():
    """Verify service root metadata and documentation link."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["docs"] == "/docs"

def test_create_expense():
    """Verify creating a new expense with amount, category, and payer."""
    payload = {
        "title": "Flight to Mumbai",
        "notes": "DevOps conference travel",
        "amount": 12500.0,
        "status": "PENDING",
        "category": "TRAVEL",
        "paid_by": "Akshat"
    }
    response = client.post("/api/expenses", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["category"] == "TRAVEL"
    assert data["amount"] == 12500.0
    assert "id" in data

def test_list_expenses():
    """Verify listing all expenses from the API."""
    response = client.get("/api/expenses")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_expense_by_id():
    """Verify retrieving a single expense by its identifier."""
    # First create an expense
    created = client.post("/api/expenses", json={"title": "Team lunch", "amount": 2400.0, "category": "FOOD", "paid_by": "Alex"}).json()
    expense_id = created["id"]

    response = client.get(f"/api/expenses/{expense_id}")
    assert response.status_code == 200
    assert response.json()["id"] == expense_id
    assert response.json()["title"] == "Team lunch"

def test_update_expense():
    """Verify updating expense status and amount."""
    created = client.post("/api/expenses", json={"title": "AWS bill", "amount": 8000.0, "category": "BILLS", "paid_by": "Sara"}).json()
    expense_id = created["id"]

    update_payload = {"status": "PAID", "amount": 8500.0}
    response = client.put(f"/api/expenses/{expense_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["status"] == "PAID"
    assert response.json()["amount"] == 8500.0

def test_expense_stats():
    """Verify aggregation endpoint returns valid metric counts and spend."""
    response = client.get("/api/expenses/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "total" in stats
    assert "pending" in stats
    assert "approved" in stats
    assert "paid" in stats
    assert "total_spend" in stats
    assert stats["total_spend"] >= 0

def test_delete_expense():
    """Verify deleting an expense removes it permanently."""
    created = client.post("/api/expenses", json={"title": "Temporary expense", "amount": 100.0, "category": "OTHER", "paid_by": "Tester"}).json()
    expense_id = created["id"]

    del_resp = client.delete(f"/api/expenses/{expense_id}")
    assert del_resp.status_code == 204

    get_resp = client.get(f"/api/expenses/{expense_id}")
    assert get_resp.status_code == 404
