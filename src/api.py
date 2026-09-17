"""FastAPI interface for the Enterprise Agentic DevOps platform."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.agent.multi_agent_orchestrator import MultiAgentOrchestrator


app = FastAPI(
    title="Enterprise Agentic DevOps API",
    description=(
        "Agentic incident analysis, decision, remediation, "
        "guardrails, observability, and evaluation API."
    ),
    version="1.0.0",
)


class IncidentRequest(BaseModel):
    """Incident payload submitted to the agentic workflow."""

    status: str = Field(
        default="incident_detected",
        description="Current incident status.",
    )

    pod: str = Field(
        ...,
        min_length=1,
        description="Affected Kubernetes pod or workload.",
    )

    root_cause: str = Field(
        ...,
        min_length=1,
        description="Observed or suspected incident root cause.",
    )

    recommendation: str = Field(
        default="",
        description="Initial operational recommendation.",
    )

    human_approved: bool = Field(
        default=False,
        description=(
            "Explicit human approval for remediation execution."
        ),
    )


@app.get("/health")
def health() -> dict[str, str]:
    """Return API health status."""

    return {
        "status": "healthy",
        "service": "enterprise-agentic-devops",
    }


@app.post("/incident")
def process_incident(
    request: IncidentRequest,
) -> dict[str, Any]:
    """
    Execute the complete agentic incident workflow.

    The workflow includes:
    analyzer -> LLM reasoning -> deterministic decision ->
    remediation -> guardrails -> reviewer/human approval ->
    observability -> evaluation/audit.
    """

    incident = {
        "status": request.status,
        "pod": request.pod,
        "root_cause": request.root_cause,
        "recommendation": request.recommendation,
    }

    try:
        orchestrator = MultiAgentOrchestrator()

        result = orchestrator.run(
            incident=incident,
            human_approved=request.human_approved,
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Agentic incident workflow failed: "
                f"{exc}"
            ),
        ) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )