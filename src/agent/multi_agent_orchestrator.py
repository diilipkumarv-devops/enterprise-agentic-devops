"""Multi-agent orchestration for the Enterprise Agentic DevOps platform."""

from src.agent.decision_engine import make_incident_decision
from src.agent.remediation import (
    build_remediation_plan,
    request_human_approval,
    simulate_remediation,
)


class AnalyzerAgent:
    """Analyzes incident evidence and prepares structured findings."""

    def run(self, incident: dict) -> dict:
        return {
            "agent": "analyzer",
            "status": "completed",
            "incident": incident,
        }


class DecisionAgent:
    """Determines incident severity, confidence, and next action."""

    def run(self, incident: dict) -> dict:
        decision = make_incident_decision(incident)

        return {
            "agent": "decision",
            "status": "completed",
            "decision": decision,
        }


class RemediationAgent:
    """Creates a safe remediation proposal."""

    def run(self, incident: dict, decision: dict) -> dict:
        if decision["decision"] != "request_remediation":
            return {
                "agent": "remediation",
                "status": "skipped",
                "plan": None,
            }

        plan = build_remediation_plan(incident)

        return {
            "agent": "remediation",
            "status": "completed",
            "plan": plan,
        }


class ReviewerAgent:
    """Applies policy and human approval before execution."""

    def run(
        self,
        remediation_plan: dict | None,
        human_approved: bool = False,
    ) -> dict:

        if remediation_plan is None:
            return {
                "agent": "reviewer",
                "status": "skipped",
                "approval": None,
                "execution": None,
            }

        approval = request_human_approval(
            remediation_plan,
            approved=human_approved,
        )

        execution = simulate_remediation(approval)

        return {
            "agent": "reviewer",
            "status": "completed",
            "approval": approval,
            "execution": execution,
        }


class MultiAgentOrchestrator:
    """Coordinates specialized agents for incident remediation."""

    def __init__(self) -> None:
        self.analyzer = AnalyzerAgent()
        self.decision_agent = DecisionAgent()
        self.remediation_agent = RemediationAgent()
        self.reviewer_agent = ReviewerAgent()

    def run(
        self,
        incident: dict,
        human_approved: bool = False,
    ) -> dict:
        """Execute the multi-agent incident workflow."""

        analyzer_result = self.analyzer.run(incident)

        decision_result = self.decision_agent.run(
            analyzer_result["incident"]
        )

        remediation_result = self.remediation_agent.run(
            analyzer_result["incident"],
            decision_result["decision"],
        )

        reviewer_result = self.reviewer_agent.run(
            remediation_result["plan"],
            human_approved=human_approved,
        )

        return {
            "incident": analyzer_result["incident"],
            "analyzer": analyzer_result,
            "decision_agent": decision_result,
            "remediation_agent": remediation_result,
            "reviewer_agent": reviewer_result,
        }


if __name__ == "__main__":
    example_incident = {
        "status": "incident_detected",
        "pod": "payment-gateway-processor-x92",
        "root_cause": (
            "The application cannot authenticate with its "
            "relational database backend."
        ),
        "recommendation": (
            "Validate the database credentials and secret configuration. "
            "Do not automatically modify production credentials "
            "without human approval."
        ),
    }

    orchestrator = MultiAgentOrchestrator()

    result = orchestrator.run(
        incident=example_incident,
        human_approved=False,
    )

    print("\n=== MULTI-AGENT DEVOPS WORKFLOW ===")

    print("\n--- ANALYZER AGENT ---")
    print(result["analyzer"])

    print("\n--- DECISION AGENT ---")
    print(result["decision_agent"])

    print("\n--- REMEDIATION AGENT ---")
    print(result["remediation_agent"])

    print("\n--- REVIEWER / POLICY AGENT ---")
    print(result["reviewer_agent"])