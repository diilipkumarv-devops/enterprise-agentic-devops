"""Multi-agent orchestration for the Enterprise Agentic DevOps platform."""

from src.agent.decision_engine import make_incident_decision
from src.agent.llm_reasoning import LLMReasoningService
from src.agent.observability import WorkflowObserver, start_timer
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


class LLMReasoningAgent:
    """
    Uses an LLM to generate advisory incident reasoning.

    The LLM does not authorize or execute remediation.
    """

    def __init__(self) -> None:
        self.service = LLMReasoningService()

    def run(self, incident: dict) -> dict:
        reasoning = self.service.reason(incident)

        return {
            "agent": "llm_reasoning",
            "status": reasoning.get("status", "unknown"),
            "reasoning": reasoning,
        }


class DecisionAgent:
    """
    Applies deterministic decision policy.

    This remains authoritative even when LLM reasoning is available.
    """

    def run(
        self,
        incident: dict,
        llm_reasoning: dict | None = None,
    ) -> dict:

        decision = make_incident_decision(incident)

        return {
            "agent": "decision",
            "status": "completed",
            "decision": decision,
            "llm_advisory_available": (
                llm_reasoning is not None
                and llm_reasoning.get("status") == "completed"
            ),
        }


class RemediationAgent:
    """Creates a safe remediation proposal."""

    def run(
        self,
        incident: dict,
        decision: dict,
    ) -> dict:

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
        self.llm_reasoning_agent = LLMReasoningAgent()
        self.decision_agent = DecisionAgent()
        self.remediation_agent = RemediationAgent()
        self.reviewer_agent = ReviewerAgent()

    def run(
        self,
        incident: dict,
        human_approved: bool = False,
    ) -> dict:
        """Execute the observable multi-agent incident workflow."""

        # Create one observer for the complete workflow.
        observer = WorkflowObserver()

        # ---------------------------------------------------------
        # STEP 1 - Analyzer Agent
        # ---------------------------------------------------------
        started_at = start_timer()

        analyzer_result = self.analyzer.run(incident)

        observer.record_agent(
            agent="analyzer",
            started_at=started_at,
            status=analyzer_result["status"],
            metadata={
                "incident_status": incident.get("status"),
                "target": incident.get("pod"),
            },
        )

        # ---------------------------------------------------------
        # STEP 2 - LLM Reasoning Agent
        # ---------------------------------------------------------
        started_at = start_timer()

        llm_result = self.llm_reasoning_agent.run(
            analyzer_result["incident"]
        )

        observer.record_agent(
            agent="llm_reasoning",
            started_at=started_at,
            status=llm_result["status"],
            metadata={
                "confidence": (
                    llm_result["reasoning"].get("confidence")
                ),
            },
        )

        # ---------------------------------------------------------
        # STEP 3 - Decision Agent
        # ---------------------------------------------------------
        started_at = start_timer()

        decision_result = self.decision_agent.run(
            analyzer_result["incident"],
            llm_reasoning=llm_result["reasoning"],
        )

        observer.record_agent(
            agent="decision",
            started_at=started_at,
            status=decision_result["status"],
            metadata={
                "severity": (
                    decision_result["decision"].get("severity")
                ),
                "decision": (
                    decision_result["decision"].get("decision")
                ),
                "requires_human_approval": (
                    decision_result["decision"].get(
                        "requires_human_approval"
                    )
                ),
            },
        )

        # ---------------------------------------------------------
        # STEP 4 - Remediation Agent
        # ---------------------------------------------------------
        started_at = start_timer()

        remediation_result = self.remediation_agent.run(
            analyzer_result["incident"],
            decision_result["decision"],
        )

        remediation_plan = remediation_result["plan"]

        observer.record_agent(
            agent="remediation",
            started_at=started_at,
            status=remediation_result["status"],
            metadata={
                "action_required": (
                    remediation_plan.get("action_required")
                    if remediation_plan
                    else False
                ),
                "risk_level": (
                    remediation_plan.get("risk_level")
                    if remediation_plan
                    else None
                ),
            },
        )

        # ---------------------------------------------------------
        # STEP 5 - Reviewer / Policy Agent
        # ---------------------------------------------------------
        started_at = start_timer()

        reviewer_result = self.reviewer_agent.run(
            remediation_plan,
            human_approved=human_approved,
        )

        approval = reviewer_result["approval"]
        execution = reviewer_result["execution"]

        observer.record_agent(
            agent="reviewer",
            started_at=started_at,
            status=reviewer_result["status"],
            metadata={
                "approval_status": (
                    approval.get("approval_status")
                    if approval
                    else None
                ),
                "execution_status": (
                    execution.get("execution_status")
                    if execution
                    else None
                ),
            },
        )

        # ---------------------------------------------------------
        # STEP 6 - Workflow Observability Summary
        # ---------------------------------------------------------
        observability = observer.summary()

        return {
            "incident": analyzer_result["incident"],
            "analyzer": analyzer_result,
            "llm_reasoning_agent": llm_result,
            "decision_agent": decision_result,
            "remediation_agent": remediation_result,
            "reviewer_agent": reviewer_result,
            "observability": observability,
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

    print(
        "\n=== OBSERVABLE LLM-ENHANCED "
        "MULTI-AGENT DEVOPS WORKFLOW ==="
    )

    print("\n--- ANALYZER AGENT ---")
    print(result["analyzer"])

    print("\n--- LLM REASONING AGENT ---")
    print(result["llm_reasoning_agent"])

    print("\n--- DECISION AGENT ---")
    print(result["decision_agent"])

    print("\n--- REMEDIATION AGENT ---")
    print(result["remediation_agent"])

    print("\n--- REVIEWER / POLICY AGENT ---")
    print(result["reviewer_agent"])

    print("\n--- OBSERVABILITY ---")

    observability = result["observability"]

    print(
        f"workflow_id: "
        f"{observability['workflow_id']}"
    )

    print(
        f"total_duration_ms: "
        f"{observability['total_duration_ms']}"
    )

    print(
        f"agent_count: "
        f"{observability['agent_count']}"
    )

    print(
        f"completed_agents: "
        f"{observability['completed_agents']}"
    )

    print(
        f"failed_agents: "
        f"{observability['failed_agents']}"
    )

    print("\n--- AGENT TRACES ---")

    for trace in observability["traces"]:
        print(trace)