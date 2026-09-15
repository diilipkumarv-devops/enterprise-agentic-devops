"""Enterprise Agentic DevOps incident orchestration workflow."""

import asyncio
import re

from src.agent.decision_engine import make_incident_decision
from src.agent.multi_agent_orchestrator import MultiAgentOrchestrator
from src.agent.mcp_client import (
    get_system_health,
    get_incident_logs,
)

from src.agent.remediation import (
    build_remediation_plan,
    request_human_approval,
    simulate_remediation,
)


def extract_failing_pod(health_report: str) -> str | None:
    """Extract the failing Kubernetes pod name from the health report."""

    match = re.search(
        r"Pod '([^']+)'",
        health_report,
    )

    if match:
        return match.group(1)

    return None


def analyze_incident(
    health_report: str,
    incident_logs: str,
) -> dict[str, str]:
    """Analyze infrastructure observations and determine root cause."""

    failing_pod = extract_failing_pod(health_report)

    if not failing_pod:
        return {
            "status": "healthy",
            "root_cause": "No failing Kubernetes pod detected.",
            "recommendation": "No remediation required.",
        }

    if "SQL_AUTHENTICATION_FAILED" in incident_logs:
        root_cause = (
            "The application cannot authenticate with its "
            "relational database backend."
        )

        recommendation = (
            "Validate the database credentials and secret configuration. "
            "Do not automatically rotate or modify production credentials "
            "without human approval."
        )

    else:
        root_cause = (
            "The exact root cause could not be determined "
            "from the available logs."
        )

        recommendation = (
            "Escalate the incident for additional log, metric, "
            "and infrastructure analysis."
        )

    return {
        "status": "incident_detected",
        "pod": failing_pod,
        "root_cause": root_cause,
        "recommendation": recommendation,
    }


async def run_incident_workflow(
    human_approved: bool = False,
) -> dict:
    """
    Run the complete MCP-driven Agentic DevOps incident workflow.

    Workflow:
    1. Inspect infrastructure health through MCP.
    2. Detect the failing Kubernetes pod.
    3. Retrieve incident logs through MCP.
    4. Perform root-cause analysis.
    5. Let the agent decision engine classify the incident.
    6. Build a remediation proposal.
    7. Apply the human approval gate.
    8. Simulate remediation only when approved.
    """

    # STEP 1 - Observe infrastructure through MCP.
    health_report = await get_system_health()

    # STEP 2 - Detect failing workload.
    failing_pod = extract_failing_pod(health_report)

    if not failing_pod:
        return {
            "incident": {
                "status": "healthy",
                "root_cause": "No failing Kubernetes pod detected.",
                "recommendation": "No remediation required.",
            },
            "agent_decision": {
                "severity": "none",
                "confidence": 1.0,
                "decision": "no_action",
                "target": None,
                "requires_human_approval": False,
                "reason": "No infrastructure incident was detected.",
            },
            "remediation_plan": None,
            "approval": None,
            "execution": None,
        }

    # STEP 3 - Retrieve logs through MCP.
    incident_logs = await get_incident_logs(failing_pod)

    # STEP 4 - Perform root-cause analysis.
    incident = analyze_incident(
        health_report=health_report,
        incident_logs=incident_logs,
    )

    # STEP 5 - Agent decision engine.
    agent_decision = make_incident_decision(incident)

    # STEP 6 - Generate remediation proposal.
    remediation_plan = build_remediation_plan(incident)

    # STEP 7 - Apply human approval policy.
    approval = request_human_approval(
        remediation_plan,
        approved=human_approved,
    )

    # STEP 8 - Execute SAFE remediation simulation.
    execution = simulate_remediation(approval)

    return {
        "incident": incident,
        "agent_decision": agent_decision,
        "remediation_plan": remediation_plan,
        "approval": approval,
        "execution": execution,
    }
async def run_multi_agent_incident_workflow(
    human_approved: bool = False,
) -> dict:
    """
    Collect real incident evidence through MCP and process it
    through the multi-agent orchestration layer.
    """

    # STEP 1 - Observe infrastructure through MCP.
    health_report = await get_system_health()

    # STEP 2 - Detect failing Kubernetes workload.
    failing_pod = extract_failing_pod(health_report)

    if not failing_pod:
        incident = {
            "status": "healthy",
            "root_cause": "No failing Kubernetes pod detected.",
            "recommendation": "No remediation required.",
        }

    else:
        # STEP 3 - Retrieve real incident logs through MCP.
        incident_logs = await get_incident_logs(failing_pod)

        # STEP 4 - Convert MCP evidence into structured incident data.
        incident = analyze_incident(
            health_report=health_report,
            incident_logs=incident_logs,
        )

    # STEP 5 - Hand structured evidence to specialized agents.
    orchestrator = MultiAgentOrchestrator()

    return orchestrator.run(
        incident=incident,
        human_approved=human_approved,
    )


def print_workflow_result(result: dict) -> None:
    """Display the complete Agentic DevOps workflow result."""

    print("\n=== ENTERPRISE AGENTIC DEVOPS INCIDENT WORKFLOW ===")

    # Incident analysis
    incident = result["incident"]

    print("\n--- INCIDENT ANALYSIS ---")

    for key, value in incident.items():
        print(f"{key}: {value}")

    # Agent decision
    agent_decision = result.get("agent_decision")

    if agent_decision:
        print("\n--- AGENT DECISION ---")

        for key, value in agent_decision.items():
            print(f"{key}: {value}")

    # Remediation plan
    remediation_plan = result.get("remediation_plan")

    if remediation_plan:
        print("\n--- REMEDIATION PLAN ---")

        for key, value in remediation_plan.items():
            print(f"{key}: {value}")

    # Human approval
    approval = result.get("approval")

    if approval:
        print("\n--- HUMAN APPROVAL GATE ---")

        print(
            f"approval_status: "
            f"{approval.get('approval_status')}"
        )

        print(
            f"execution_allowed: "
            f"{approval.get('execution_allowed')}"
        )

    # Execution
    execution = result.get("execution")

    if execution:
        print("\n--- EXECUTION RESULT ---")

        for key, value in execution.items():
            print(f"{key}: {value}")


if __name__ == "__main__":

    # Demo/testing only.
    #
    # Production-changing actions must never be automatically approved.
    # Keep this False when demonstrating the safety gate.
    #  if __name__ == "__main__":

    # Production-changing actions must never be automatically approved.
    HUMAN_APPROVED = False

    workflow_result = asyncio.run(
        run_multi_agent_incident_workflow(
            human_approved=HUMAN_APPROVED,
        )
    )

    print("\n=== MCP-DRIVEN MULTI-AGENT DEVOPS WORKFLOW ===")

    print("\n--- INCIDENT ---")
    print(workflow_result["incident"])

    print("\n--- ANALYZER AGENT ---")
    print(workflow_result["analyzer"])

    print("\n--- DECISION AGENT ---")
    print(workflow_result["decision_agent"])

    print("\n--- REMEDIATION AGENT ---")
    print(workflow_result["remediation_agent"])

    print("\n--- REVIEWER / POLICY AGENT ---")
    print(workflow_result["reviewer_agent"])