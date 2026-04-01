from src.api import (
    ResetRequest,
    health,
    metadata,
    reset,
    root,
    schema,
    step,
    tasks,
)


def test_root_endpoint() -> None:
    body = root()
    assert body["status"] == "ok"
    assert "/health" in body["endpoints"]


def test_health_endpoint() -> None:
    assert health()["status"] == "healthy"


def test_metadata_endpoint() -> None:
    body = metadata().model_dump()
    assert body["name"] == "customer-support-ticket-triage"
    assert body["version"] == "0.1.0"


def test_schema_endpoint() -> None:
    body = schema().model_dump()
    assert "action" in body
    assert "observation" in body
    assert "state" in body


def test_tasks_endpoint() -> None:
    body = tasks()
    assert len(body["tasks"]) == 3
    assert "action_schema" in body


def test_reset_endpoint_accepts_empty_body() -> None:
    body = reset(ResetRequest()).model_dump()
    assert "observation" in body
    assert body["reward"] is None
    assert body["done"] is False


def test_step_endpoint_accepts_wrapped_action() -> None:
    reset(ResetRequest(task_id="refund_status_easy"))
    body = step(
        {
            "action": {
                "action_type": "set_category",
                "ticket_id": "TKT-1001",
                "value": "billing_refund",
            }
        }
    ).model_dump()
    assert "observation" in body
    assert isinstance(body["reward"], float)
    assert body["done"] is False
