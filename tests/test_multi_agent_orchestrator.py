"""Tests for Enterprise Agentic DevOps multi-agent orchestration."""

from unittest.mock import patch

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


def build_mock_llm_reasoning() -> dict:
    """Create deterministic advisory LLM reasoning for unit tests."""

    return {
        "status": "completed",
        "diagnosis": (
            "The workload cannot authenticate with its database backend."
        ),
        "reasoning_summary": (
            "The incident evidence indicates a database "
            "authentication failure."
        ),
        "recommended_action": (
            "Validate the database credentials and secret configuration."
        ),
        "confidence": 0.90,
    }


def run_orchestrator(
    human_approved: bool = False,
) -> dict:
    """
    Run the orchestrator with mocked LLM reasoning.

    Unit tests must not depend on a running Ollama service.
    """

    with patch(
        "src.agent.multi_agent_orchestrator."
        "LLMReasoningService.reason",
        return_value=build_mock_llm_reasoning(),
    ):
        orchestrator = MultiAgentOrchestrator()

        return orchestrator.run(
            incident=build_database_incident(),
            human_approved=human_approved,
        )


def test_multi_agent_decision_is_critical():
    """Decision Agent should classify DB authentication failure as critical."""

    result = run_orchestrator(
        human_approved=False,
    )

    decision = result["decision_agent"]["decision"]

    assert decision["severity"] == "critical"
    assert decision["confidence"] == 0.95
    assert decision["decision"] == "request_remediation"
    assert decision["requires_human_approval"] is True


def test_llm_advisory_is_available():
    """Decision Agent should detect successful advisory LLM reasoning."""

    result = run_orchestrator(
        human_approved=False,
    )

    llm_result = result["llm_reasoning_agent"]
    decision_agent = result["decision_agent"]

    assert llm_result["status"] == "completed"
    assert llm_result["reasoning"]["confidence"] == 0.90
    assert decision_agent["llm_advisory_available"] is True


def test_remediation_agent_builds_plan():
    """Remediation Agent should create a high-risk remediation plan."""

    result = run_orchestrator(
        human_approved=False,
    )

    remediation = result["remediation_agent"]

    assert remediation["status"] == "completed"
    assert remediation["plan"]["action_required"] is True
    assert remediation["plan"]["risk_level"] == "high"
    assert remediation["plan"]["requires_human_approval"] is True


def test_policy_blocks_unapproved_remediation():
    """Reviewer Agent must block remediation without human approval."""

    result = run_orchestrator(
        human_approved=False,
    )

    reviewer = result["reviewer_agent"]

    assert reviewer["approval"]["approval_status"] == "pending"
    assert reviewer["approval"]["execution_allowed"] is False
    assert reviewer["execution"]["execution_status"] == "blocked"


def test_policy_allows_approved_simulation():
    """Reviewer Agent should allow safe simulation after approval."""

    result = run_orchestrator(
        human_approved=True,
    )

    reviewer = result["reviewer_agent"]

    assert reviewer["approval"]["approval_status"] == "approved"
    assert reviewer["approval"]["execution_allowed"] is True
    assert reviewer["execution"]["execution_status"] == "simulated_success"