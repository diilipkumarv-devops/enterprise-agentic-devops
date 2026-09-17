"""Tests for the Enterprise Agentic DevOps FastAPI layer."""

from fastapi.testclient import TestClient

from src.api import app


client = TestClient(app)


def test_health_endpoint():
    """Health endpoint should report the API as healthy."""

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy",
        "service": "enterprise-agentic-devops",
    }


def test_incident_endpoint_returns_workflow_result(monkeypatch):
    """Incident endpoint should return orchestrator output."""

    expected_result = {
        "incident": {
            "status": "incident_detected",
            "pod": "payment-gateway-processor-x92",
            "root_cause": "Database authentication failure.",
            "recommendation": "Validate credentials.",
        },
        "decision_agent": {
            "decision": {
                "severity": "critical",
                "decision": "request_remediation",
                "requires_human_approval": True,
            }
        },
        "guardrails": {
            "guardrail_status": "passed",
            "safe_to_continue": True,
        },
        "reviewer_agent": {
            "execution": {
                "execution_status": "blocked",
            }
        },
        "evaluation": {
            "evaluation_status": "passed",
            "safe_execution": True,
        },
    }

    def fake_run(
        self,
        incident,
        human_approved=False,
    ):
        assert incident["pod"] == (
            "payment-gateway-processor-x92"
        )

        assert human_approved is False

        return expected_result

    monkeypatch.setattr(
        "src.api.MultiAgentOrchestrator.run",
        fake_run,
    )

    payload = {
        "status": "incident_detected",
        "pod": "payment-gateway-processor-x92",
        "root_cause": "Database authentication failure.",
        "recommendation": "Validate credentials.",
        "human_approved": False,
    }

    response = client.post(
        "/incident",
        json=payload,
    )

    assert response.status_code == 200
    assert response.json() == expected_result


def test_incident_endpoint_accepts_human_approval(
    monkeypatch,
):
    """Human approval should reach the orchestrator."""

    captured = {}

    def fake_run(
        self,
        incident,
        human_approved=False,
    ):
        captured["human_approved"] = human_approved

        return {
            "status": "completed",
            "human_approved": human_approved,
        }

    monkeypatch.setattr(
        "src.api.MultiAgentOrchestrator.run",
        fake_run,
    )

    payload = {
        "status": "incident_detected",
        "pod": "payment-gateway-processor-x92",
        "root_cause": "Database authentication failure.",
        "recommendation": "Validate credentials.",
        "human_approved": True,
    }

    response = client.post(
        "/incident",
        json=payload,
    )

    assert response.status_code == 200
    assert captured["human_approved"] is True

    assert response.json()["human_approved"] is True


def test_incident_endpoint_rejects_missing_pod():
    """Pod is required by the API contract."""

    payload = {
        "status": "incident_detected",
        "root_cause": "Database authentication failure.",
        "human_approved": False,
    }

    response = client.post(
        "/incident",
        json=payload,
    )

    assert response.status_code == 422


def test_incident_endpoint_rejects_empty_root_cause():
    """Root cause cannot be an empty string."""

    payload = {
        "status": "incident_detected",
        "pod": "payment-gateway-processor-x92",
        "root_cause": "",
        "human_approved": False,
    }

    response = client.post(
        "/incident",
        json=payload,
    )

    assert response.status_code == 422


def test_incident_endpoint_handles_workflow_failure(
    monkeypatch,
):
    """Unexpected workflow errors should become HTTP 500."""

    def fake_run(
        self,
        incident,
        human_approved=False,
    ):
        raise RuntimeError(
            "Simulated orchestrator failure"
        )

    monkeypatch.setattr(
        "src.api.MultiAgentOrchestrator.run",
        fake_run,
    )

    payload = {
        "status": "incident_detected",
        "pod": "payment-gateway-processor-x92",
        "root_cause": "Database authentication failure.",
        "recommendation": "Validate credentials.",
        "human_approved": False,
    }

    response = client.post(
        "/incident",
        json=payload,
    )

    assert response.status_code == 500

    assert (
        "Agentic incident workflow failed"
        in response.json()["detail"]
    )