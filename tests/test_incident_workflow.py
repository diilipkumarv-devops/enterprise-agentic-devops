"""Tests for the Enterprise Agentic DevOps incident workflow."""

from src.agent.incident_orchestrator import (
    analyze_incident,
    extract_failing_pod,
)
from src.agent.remediation import (
    build_remediation_plan,
    request_human_approval,
    simulate_remediation,
)


HEALTH_REPORT = (
    "=== CLUSTER HEALTH AUDIT REPORT ===\n"
    "CRITICAL ALERT DETECTED: "
    "Pod 'payment-gateway-processor-x92' "
    "is stuck in a 'CrashLoopBackOff' state "
    "inside namespace 'production'."
)

INCIDENT_LOGS = (
    "[FATAL] SQL_AUTHENTICATION_FAILED: "
    "Credential string validation failed."
)


def test_extract_failing_pod():
    """The failing Kubernetes pod should be extracted correctly."""

    pod = extract_failing_pod(HEALTH_REPORT)

    assert pod == "payment-gateway-processor-x92"


def test_incident_root_cause_analysis():
    """SQL authentication failures should produce the expected RCA."""

    result = analyze_incident(
        HEALTH_REPORT,
        INCIDENT_LOGS,
    )

    assert result["status"] == "incident_detected"
    assert result["pod"] == "payment-gateway-processor-x92"
    assert "authenticate" in result["root_cause"].lower()


def test_remediation_plan_requires_human_approval():
    """High-risk credential remediation must require human approval."""

    incident = analyze_incident(
        HEALTH_REPORT,
        INCIDENT_LOGS,
    )

    plan = build_remediation_plan(incident)

    assert plan["action_required"] is True
    assert plan["risk_level"] == "high"
    assert plan["requires_human_approval"] is True


def test_remediation_blocked_without_approval():
    """Execution must be blocked when approval has not been granted."""

    incident = analyze_incident(
        HEALTH_REPORT,
        INCIDENT_LOGS,
    )

    plan = build_remediation_plan(incident)

    gated_plan = request_human_approval(
        plan,
        approved=False,
    )

    result = simulate_remediation(gated_plan)

    assert gated_plan["approval_status"] == "pending"
    assert gated_plan["execution_allowed"] is False
    assert result["execution_status"] == "blocked"


def test_remediation_allowed_after_approval():
    """Approved remediation should execute only in simulation mode."""

    incident = analyze_incident(
        HEALTH_REPORT,
        INCIDENT_LOGS,
    )

    plan = build_remediation_plan(incident)

    approved_plan = request_human_approval(
        plan,
        approved=True,
    )

    result = simulate_remediation(approved_plan)

    assert approved_plan["approval_status"] == "approved"
    assert approved_plan["execution_allowed"] is True
    assert result["execution_status"] == "simulated_success"
    assert result["target"] == "payment-gateway-processor-x92"