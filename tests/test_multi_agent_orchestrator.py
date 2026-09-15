"""Tests for Enterprise Agentic DevOps multi-agent orchestration."""

from src.agent.multi_agent_orchestrator import MultiAgentOrchestrator


def build_database_incident() -> dict:
    """Create a reusable critical database incident."""

    return {
        "status": "incident_detected",
        "pod": "payment-gateway-processor-x92",
        "root_cause": (
            "The application cannot authenticate with its "
            "relational database backend."
        ),
        "recommendation": (
            "Validate the database credentials and secret configuration."
        ),
    }


def test_multi_agent_decision_is_critical():
    """Decision Agent should classify DB authentication failure as critical."""

    orchestrator = MultiAgentOrchestrator()

    result = orchestrator.run(
        incident=build_database_incident(),
        human_approved=False,
    )

    decision = result["decision_agent"]["decision"]

    assert decision["severity"] == "critical"
    assert decision["confidence"] == 0.95
    assert decision["decision"] == "request_remediation"
    assert decision["requires_human_approval"] is True


def test_remediation_agent_builds_plan():
    """Remediation Agent should create a high-risk remediation plan."""

    orchestrator = MultiAgentOrchestrator()

    result = orchestrator.run(
        incident=build_database_incident(),
        human_approved=False,
    )

    remediation = result["remediation_agent"]

    assert remediation["status"] == "completed"
    assert remediation["plan"]["action_required"] is True
    assert remediation["plan"]["risk_level"] == "high"
    assert remediation["plan"]["requires_human_approval"] is True


def test_policy_blocks_unapproved_remediation():
    """Reviewer Agent must block remediation without human approval."""

    orchestrator = MultiAgentOrchestrator()

    result = orchestrator.run(
        incident=build_database_incident(),
        human_approved=False,
    )

    reviewer = result["reviewer_agent"]

    assert reviewer["approval"]["approval_status"] == "pending"
    assert reviewer["approval"]["execution_allowed"] is False
    assert reviewer["execution"]["execution_status"] == "blocked"


def test_policy_allows_approved_simulation():
    """Reviewer Agent should allow safe simulation after approval."""

    orchestrator = MultiAgentOrchestrator()

    result = orchestrator.run(
        incident=build_database_incident(),
        human_approved=True,
    )

    reviewer = result["reviewer_agent"]

    assert reviewer["approval"]["approval_status"] == "approved"
    assert reviewer["approval"]["execution_allowed"] is True
    assert reviewer["execution"]["execution_status"] == "simulated_success"