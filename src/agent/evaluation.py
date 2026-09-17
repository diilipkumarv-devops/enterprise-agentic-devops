"""Evaluation and audit utilities for Enterprise Agentic DevOps."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class WorkflowEvaluator:
    """Evaluate quality, safety, and execution of an agentic workflow."""

    def evaluate(
        self,
        workflow_result: dict[str, Any],
    ) -> dict[str, Any]:
        """Evaluate a completed workflow and produce an audit record."""

        llm_result = workflow_result.get(
            "llm_reasoning_agent",
            {},
        )
        decision_result = workflow_result.get(
            "decision_agent",
            {},
        )
        remediation_result = workflow_result.get(
            "remediation_agent",
            {},
        )
        guardrail_result = workflow_result.get(
            "guardrails",
            {},
        )
        reviewer_result = workflow_result.get(
            "reviewer_agent",
            {},
        )
        observability = workflow_result.get(
            "observability",
            {},
        )

        reasoning = llm_result.get("reasoning", {})
        decision = decision_result.get("decision", {})
        remediation = remediation_result.get("plan")
        execution = reviewer_result.get("execution") or {}

        llm_confidence = float(
            reasoning.get("confidence", 0.0)
        )

        guardrails_passed = (
            guardrail_result.get("guardrail_status")
            == "passed"
        )

        human_approval_required = bool(
            decision.get(
                "requires_human_approval",
                False,
            )
        )

        execution_status = execution.get(
            "execution_status",
            "not_executed",
        )

        failed_agents = int(
            observability.get("failed_agents", 0)
        )

        checks = {
            "llm_reasoning_completed": (
                reasoning.get("status") == "completed"
            ),
            "llm_confidence_acceptable": (
                llm_confidence >= 0.70
            ),
            "guardrails_passed": guardrails_passed,
            "no_agent_failures": failed_agents == 0,
            "critical_action_requires_approval": (
                decision.get("severity") != "critical"
                or human_approval_required
            ),
        }

        passed_checks = sum(checks.values())
        total_checks = len(checks)

        quality_score = round(
            passed_checks / total_checks,
            2,
        )

        safe_outcomes = {
            "blocked",
            "simulated_success",
            "not_executed",
        }

        safe_execution = (
            execution_status in safe_outcomes
        )

        overall_passed = (
            all(checks.values())
            and safe_execution
        )

        audit_record = {
            "timestamp_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "workflow_id": observability.get(
                "workflow_id"
            ),
            "severity": decision.get("severity"),
            "decision": decision.get("decision"),
            "llm_confidence": llm_confidence,
            "guardrail_status": guardrail_result.get(
                "guardrail_status"
            ),
            "human_approval_required": (
                human_approval_required
            ),
            "execution_status": execution_status,
            "failed_agents": failed_agents,
        }

        return {
            "evaluation_status": (
                "passed"
                if overall_passed
                else "failed"
            ),
            "quality_score": quality_score,
            "safe_execution": safe_execution,
            "checks": checks,
            "audit_record": audit_record,
        }


if __name__ == "__main__":

    evaluator = WorkflowEvaluator()

    example_workflow = {
        "llm_reasoning_agent": {
            "reasoning": {
                "status": "completed",
                "confidence": 0.80,
            }
        },
        "decision_agent": {
            "decision": {
                "severity": "critical",
                "decision": "request_remediation",
                "requires_human_approval": True,
            }
        },
        "remediation_agent": {
            "plan": {
                "risk_level": "high",
            }
        },
        "guardrails": {
            "guardrail_status": "passed",
        },
        "reviewer_agent": {
            "execution": {
                "execution_status": "blocked",
            }
        },
        "observability": {
            "workflow_id": "demo-workflow-001",
            "failed_agents": 0,
        },
    }

    result = evaluator.evaluate(
        example_workflow
    )

    print(
        "\n=== AGENTIC DEVOPS WORKFLOW EVALUATION ==="
    )

    print(
        f"evaluation_status: "
        f"{result['evaluation_status']}"
    )

    print(
        f"quality_score: "
        f"{result['quality_score']}"
    )

    print(
        f"safe_execution: "
        f"{result['safe_execution']}"
    )

    print("\n--- QUALITY / SAFETY CHECKS ---")

    for check, passed in result["checks"].items():
        print(f"{check}: {passed}")

    print("\n--- AUDIT RECORD ---")

    for key, value in result["audit_record"].items():
        print(f"{key}: {value}")