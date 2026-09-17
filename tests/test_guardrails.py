"""Tests for Enterprise Agentic DevOps guardrails."""

from src.agent.guardrails import AgentGuardrails
from src.agent.decision_engine import make_incident_decision
from src.agent.guardrails import AgentGuardrails
from src.agent.llm_reasoning import LLMReasoningService
from src.agent.observability import WorkflowObserver, start_timer
from src.agent.remediation import (
    build_remediation_plan,
    request_human_approval,
    simulate_remediation,
)

def test_safe_workflow_passes_guardrails():
    guardrails = AgentGuardrails()

    llm_reasoning = {
        "status": "completed",
        "confidence": 0.80,
    }

    decision = {
        "severity": "critical",
        "decision": "request_remediation",
        "requires_human_approval": True,
    }

    remediation = {
        "risk_level": "high",
        "requires_human_approval": True,
    }

    result = guardrails.evaluate_workflow(
        llm_reasoning,
        decision,
        remediation,
    )

    assert result["guardrail_status"] == "passed"
    assert result["safe_to_continue"] is True
    assert result["violations"] == []


def test_low_llm_confidence_blocks_workflow():
    guardrails = AgentGuardrails(
        minimum_llm_confidence=0.70
    )

    llm_reasoning = {
        "status": "completed",
        "confidence": 0.40,
    }

    decision = {
        "severity": "medium",
        "decision": "escalate",
        "requires_human_approval": True,
    }

    result = guardrails.evaluate_workflow(
        llm_reasoning,
        decision,
        None,
    )

    assert result["guardrail_status"] == "blocked"
    assert result["safe_to_continue"] is False

    assert (
        "llm_confidence_below_threshold"
        in result["violations"]
    )


def test_critical_incident_without_approval_is_blocked():
    guardrails = AgentGuardrails()

    decision = {
        "severity": "critical",
        "decision": "request_remediation",
        "requires_human_approval": False,
    }

    result = guardrails.evaluate_decision(decision)

    assert result["passed"] is False

    assert (
        "critical_incident_missing_human_approval"
        in result["violations"]
    )


def test_high_risk_remediation_without_approval_is_blocked():
    guardrails = AgentGuardrails()

    remediation = {
        "risk_level": "high",
        "requires_human_approval": False,
    }

    result = guardrails.evaluate_remediation(remediation)

    assert result["passed"] is False

    assert (
        "high_risk_remediation_missing_human_approval"
        in result["violations"]
    )


def test_incomplete_llm_reasoning_is_blocked():
    guardrails = AgentGuardrails()

    reasoning = {
        "status": "failed",
        "confidence": 0.90,
    }

    result = guardrails.evaluate_llm_reasoning(reasoning)

    assert result["passed"] is False

    assert (
        "llm_reasoning_incomplete"
        in result["violations"]
    )

    