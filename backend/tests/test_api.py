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

def test_create_task():
    """Verify creating a new task with status, priority, and assignee."""
    payload = {
        "title": "Configure EKS Terraform Module",
        "description": "Provision VPC, subnets, and worker node group",
        "status": "TODO",
        "priority": "HIGH",
        "assignee": "DevOps Engineer"
    }
    response = client.post("/api/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["priority"] == "HIGH"
    assert "id" in data

def test_list_tasks():
    """Verify listing all tasks from the API."""
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_task_by_id():
    """Verify retrieving a single task by its identifier."""
    # First create a task
    created = client.post("/api/tasks", json={"title": "Setup Ingress Controller", "priority": "MEDIUM", "assignee": "Alex"}).json()
    task_id = created["id"]

    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id
    assert response.json()["title"] == "Setup Ingress Controller"

def test_update_task():
    """Verify updating task status and priority."""
    created = client.post("/api/tasks", json={"title": "Fix Broken Service", "priority": "LOW", "assignee": "Sara"}).json()
    task_id = created["id"]

    update_payload = {"status": "DONE", "priority": "HIGH"}
    response = client.put(f"/api/tasks/{task_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["status"] == "DONE"
    assert response.json()["priority"] == "HIGH"

def test_task_stats():
    """Verify aggregation endpoint returns valid metric counts."""
    response = client.get("/api/tasks/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "total" in stats
    assert "todo" in stats
    assert "inProgress" in stats
    assert "done" in stats

def test_delete_task():
    """Verify deleting a task removes it permanently."""
    created = client.post("/api/tasks", json={"title": "Temporary Task", "priority": "LOW", "assignee": "Tester"}).json()
    task_id = created["id"]

    del_resp = client.delete(f"/api/tasks/{task_id}")
    assert del_resp.status_code == 204

    get_resp = client.get(f"/api/tasks/{task_id}")
    assert get_resp.status_code == 404
