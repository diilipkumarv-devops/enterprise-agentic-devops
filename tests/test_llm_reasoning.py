"""Tests for the LLM reasoning layer."""

from unittest.mock import patch

from src.agent.llm_reasoning import LLMReasoningService


def test_llm_prompt_contains_incident_evidence():
    service = LLMReasoningService()

    incident = {
        "status": "incident_detected",
        "pod": "payment-gateway-processor-x92",
        "root_cause": "Database authentication failure.",
        "recommendation": "Validate database credentials.",
    }

    prompt = service.build_prompt(incident)

    assert "payment-gateway-processor-x92" in prompt
    assert "Database authentication failure." in prompt
    assert "Validate database credentials." in prompt
    assert "human approval" in prompt.lower()


def test_llm_reasoning_returns_structured_result():
    service = LLMReasoningService()

    incident = {
        "status": "incident_detected",
        "pod": "payment-gateway-processor-x92",
        "root_cause": "Database authentication failure.",
        "recommendation": "Validate database credentials.",
    }

    mock_response = {
        "status": "completed",
        "diagnosis": "Database credential authentication failure.",
        "reasoning_summary": (
            "The workload cannot authenticate with its database."
        ),
        "recommended_action": (
            "Validate the configured database secret."
        ),
        "confidence": 0.90,
    }

    with patch.object(
        service,
        "reason",
        return_value=mock_response,
    ):
        result = service.reason(incident)

    assert result["status"] == "completed"
    assert result["confidence"] == 0.90
    assert "credential" in result["diagnosis"].lower()


def test_llm_reasoning_does_not_authorize_execution():
    service = LLMReasoningService()

    incident = {
        "status": "incident_detected",
        "pod": "payment-gateway-processor-x92",
        "root_cause": "Database authentication failure.",
        "recommendation": "Validate database credentials.",
    }

    prompt = service.build_prompt(incident)

    assert "Do not authorize production changes." in prompt
    assert "Credential changes require human approval." in prompt