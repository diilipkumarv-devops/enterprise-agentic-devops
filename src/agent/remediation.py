"""Safe remediation planning for the Enterprise Agentic DevOps platform."""


def build_remediation_plan(
    incident: dict[str, str],
) -> dict[str, str | bool]:
    """Build a remediation proposal without executing any production change."""

    if incident.get("status") != "incident_detected":
        return {
            "action_required": False,
            "risk_level": "none",
            "proposed_action": "No remediation required.",
            "requires_human_approval": False,
        }

    root_cause = incident.get("root_cause", "")
    pod = incident.get("pod", "unknown")

    if "cannot authenticate" in root_cause.lower():
        return {
            "action_required": True,
            "risk_level": "high",
            "target": pod,
            "proposed_action": (
                "Validate the database secret configuration and prepare "
                "a controlled credential remediation for the affected workload."
            ),
            "requires_human_approval": True,
        }

    return {
        "action_required": True,
        "risk_level": "medium",
        "target": pod,
        "proposed_action": (
            "Escalate the incident for additional investigation."
        ),
        "requires_human_approval": True,
    }


def request_human_approval(
    remediation_plan: dict[str, str | bool],
    approved: bool = False,
) -> dict[str, str | bool]:
    """Apply a human approval gate before remediation can proceed."""

    if not remediation_plan.get("action_required"):
        return {
            **remediation_plan,
            "approval_status": "not_required",
            "execution_allowed": False,
        }

    if remediation_plan.get("requires_human_approval") and not approved:
        return {
            **remediation_plan,
            "approval_status": "pending",
            "execution_allowed": False,
        }

    return {
        **remediation_plan,
        "approval_status": "approved",
        "execution_allowed": True,
    }


def simulate_remediation(
    approved_plan: dict[str, str | bool],
) -> dict[str, str]:
    """Simulate remediation. This function makes no infrastructure changes."""

    if not approved_plan.get("execution_allowed"):
        return {
            "execution_status": "blocked",
            "message": (
                "Remediation blocked by policy. "
                "Explicit human approval is required."
            ),
        }

    target = approved_plan.get("target", "unknown")

    return {
        "execution_status": "simulated_success",
        "target": str(target),
        "message": (
            "Approved remediation was simulated successfully. "
            "No production infrastructure was modified."
        ),
    }