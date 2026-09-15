"""Tests for the Enterprise Agentic DevOps decision engine."""

from src.agent.decision_engine import make_incident_decision


def test_healthy_incident_requires_no_action():
    """Healthy infrastructure should require no remediation."""

    incident = {
        "status": "healthy",
        "root_cause": "No failing Kubernetes pod detected.",
        "recommendation": "No remediation required.",
    }

    decision = make_incident_decision(incident)

    assert decision["severity"] == "none"
    assert decision["confidence"] == 1.0
    assert decision["decision"] == "no_action"
    assert decision["requires_human_approval"] is False


def test_database_authentication_failure_is_critical():
    """Database authentication failure should be critical."""

    incident = {
        "status": "incident_detected",
        "pod": "payment-gateway-processor-x92",
        "root_cause": (
            "The application cannot authenticate with its "
            "relational database backend."
        ),
        "recommendation": (
            "Validate database credentials and secret configuration."
        ),
    }

    decision = make_incident_decision(incident)

    assert decision["severity"] == "critical"
    assert decision["confidence"] == 0.95
    assert decision["decision"] == "request_remediation"
    assert decision["target"] == "payment-gateway-processor-x92"
    assert decision["requires_human_approval"] is True


def test_unknown_incident_is_escalated():
    """Unknown incidents should be escalated rather than auto-remediated."""

    incident = {
        "status": "incident_detected",
        "pod": "unknown-service-x01",
        "root_cause": (
            "The exact root cause could not be determined "
            "from the available logs."
        ),
        "recommendation": (
            "Escalate for additional investigation."
        ),
    }

    decision = make_incident_decision(incident)

    assert decision["severity"] == "medium"
    assert decision["confidence"] == 0.60
    assert decision["decision"] == "escalate"
    assert decision["target"] == "unknown-service-x01"
    assert decision["requires_human_approval"] is True