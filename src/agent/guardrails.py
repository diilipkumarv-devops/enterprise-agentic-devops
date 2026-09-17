"""Safety guardrails for the Enterprise Agentic DevOps platform."""

from typing import Any


class AgentGuardrails:
    """
    Evaluates agent outputs before remediation is allowed to proceed.

    Guardrails are deterministic and remain authoritative.
    LLM recommendations are advisory only.
    """

    def __init__(
        self,
        minimum_llm_confidence: float = 0.70,
    ) -> None:
        self.minimum_llm_confidence = minimum_llm_confidence

    def evaluate_llm_reasoning(
        self,
        reasoning: dict[str, Any],
    ) -> dict[str, Any]:
        """Validate LLM reasoning quality and confidence."""

        confidence = float(reasoning.get("confidence", 0.0))
        status = reasoning.get("status", "unknown")

        violations: list[str] = []

        if status != "completed":
            violations.append("llm_reasoning_incomplete")

        if confidence < self.minimum_llm_confidence:
            violations.append("llm_confidence_below_threshold")

        return {
            "check": "llm_reasoning",
            "passed": len(violations) == 0,
            "confidence": confidence,
            "minimum_confidence": self.minimum_llm_confidence,
            "violations": violations,
        }

    def evaluate_decision(
        self,
        decision: dict[str, Any],
    ) -> dict[str, Any]:
        """Validate the deterministic incident decision."""

        violations: list[str] = []

        severity = decision.get("severity", "unknown")
        action = decision.get("decision", "unknown")
        requires_approval = decision.get(
            "requires_human_approval",
            False,
        )

        if severity == "critical" and not requires_approval:
            violations.append(
                "critical_incident_missing_human_approval"
            )

        if action == "request_remediation" and severity == "critical":
            if not requires_approval:
                violations.append(
                    "critical_remediation_cannot_auto_execute"
                )

        return {
            "check": "decision_policy",
            "passed": len(violations) == 0,
            "severity": severity,
            "decision": action,
            "requires_human_approval": requires_approval,
            "violations": violations,
        }

    def evaluate_remediation(
        self,
        remediation_plan: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Validate remediation risk and approval requirements."""

        if remediation_plan is None:
            return {
                "check": "remediation_policy",
                "passed": True,
                "violations": [],
                "message": "No remediation plan requires evaluation.",
            }

        violations: list[str] = []

        risk_level = remediation_plan.get(
            "risk_level",
            "unknown",
        )

        requires_approval = remediation_plan.get(
            "requires_human_approval",
            False,
        )

        if risk_level == "high" and not requires_approval:
            violations.append(
                "high_risk_remediation_missing_human_approval"
            )

        return {
            "check": "remediation_policy",
            "passed": len(violations) == 0,
            "risk_level": risk_level,
            "requires_human_approval": requires_approval,
            "violations": violations,
        }

    def evaluate_workflow(
        self,
        llm_reasoning: dict[str, Any],
        decision: dict[str, Any],
        remediation_plan: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Run all guardrails and produce one workflow verdict."""

        checks = [
            self.evaluate_llm_reasoning(llm_reasoning),
            self.evaluate_decision(decision),
            self.evaluate_remediation(remediation_plan),
        ]

        violations = [
            violation
            for check in checks
            for violation in check["violations"]
        ]

        passed = all(check["passed"] for check in checks)

        return {
            "guardrail_status": (
                "passed" if passed else "blocked"
            ),
            "safe_to_continue": passed,
            "checks": checks,
            "violations": violations,
        }


if __name__ == "__main__":
    guardrails = AgentGuardrails()

    example_llm_reasoning = {
        "status": "completed",
        "diagnosis": (
            "Database authentication failure detected."
        ),
        "confidence": 0.80,
    }

    example_decision = {
        "severity": "critical",
        "confidence": 0.95,
        "decision": "request_remediation",
        "target": "payment-gateway-processor-x92",
        "requires_human_approval": True,
    }

    example_remediation = {
        "action_required": True,
        "risk_level": "high",
        "target": "payment-gateway-processor-x92",
        "requires_human_approval": True,
    }

    result = guardrails.evaluate_workflow(
        llm_reasoning=example_llm_reasoning,
        decision=example_decision,
        remediation_plan=example_remediation,
    )

    print("\n=== AGENTIC DEVOPS GUARDRAILS ===")

    print(
        f"guardrail_status: "
        f"{result['guardrail_status']}"
    )

    print(
        f"safe_to_continue: "
        f"{result['safe_to_continue']}"
    )

    print("\n--- CHECKS ---")

    for check in result["checks"]:
        print(check)

    print("\n--- VIOLATIONS ---")
    print(result["violations"])