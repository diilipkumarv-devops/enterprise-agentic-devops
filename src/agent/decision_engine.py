"""Decision engine for the Enterprise Agentic DevOps platform."""


def make_incident_decision(
    incident: dict[str, str],
) -> dict[str, object]:
    """Evaluate an analyzed incident and determine the next safe action."""

    status = incident.get("status", "unknown")
    root_cause = incident.get("root_cause", "")
    pod = incident.get("pod", "unknown")

    if status == "healthy":
        return {
            "severity": "none",
            "confidence": 1.0,
            "decision": "no_action",
            "target": pod,
            "requires_human_approval": False,
            "reason": "No active infrastructure incident was detected.",
        }

    if "cannot authenticate" in root_cause.lower():
        return {
            "severity": "critical",
            "confidence": 0.95,
            "decision": "request_remediation",
            "target": pod,
            "requires_human_approval": True,
            "reason": (
                "Database authentication failure detected. "
                "Credential-related remediation is high risk."
            ),
        }

    return {
        "severity": "medium",
        "confidence": 0.60,
        "decision": "escalate",
        "target": pod,
        "requires_human_approval": True,
        "reason": (
            "The incident requires additional investigation "
            "before remediation can be attempted."
        ),
    }


if __name__ == "__main__":
    example_incident = {
        "status": "incident_detected",
        "pod": "payment-gateway-processor-x92",
        "root_cause": (
            "The application cannot authenticate with its "
            "relational database backend."
        ),
    }

    decision = make_incident_decision(example_incident)

    print("=== AGENT DECISION ===")

    for key, value in decision.items():
        print(f"{key}: {value}")