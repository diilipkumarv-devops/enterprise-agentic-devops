"""Observability utilities for the Enterprise Agentic DevOps platform."""

import time
import uuid
from typing import Any


def start_timer() -> float:
    """Return the current high-resolution timer value."""
    return time.perf_counter()


class WorkflowObserver:
    """Collect lightweight traces and metrics for an agentic workflow."""

    def __init__(self) -> None:
        self.workflow_id = str(uuid.uuid4())
        self.workflow_start = start_timer()
        self.traces: list[dict[str, Any]] = []

    def record_agent(
        self,
        agent: str,
        status: str,
        started_at: float,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record execution information for one agent."""

        duration_ms = round(
            (time.perf_counter() - started_at) * 1000,
            2,
        )

        self.traces.append(
            {
                "agent": agent,
                "status": status,
                "duration_ms": duration_ms,
                "metadata": metadata or {},
            }
        )

    def summary(self) -> dict[str, Any]:
        """Return workflow-level observability metrics."""

        total_duration_ms = round(
            (time.perf_counter() - self.workflow_start) * 1000,
            2,
        )

        completed_agents = sum(
            trace["status"] == "completed"
            for trace in self.traces
        )

        failed_agents = sum(
            trace["status"] == "failed"
            for trace in self.traces
        )

        return {
            "workflow_id": self.workflow_id,
            "total_duration_ms": total_duration_ms,
            "agent_count": len(self.traces),
            "completed_agents": completed_agents,
            "failed_agents": failed_agents,
            "traces": self.traces,
        }


if __name__ == "__main__":
    observer = WorkflowObserver()

    analyzer_start = start_timer()
    time.sleep(0.01)

    observer.record_agent(
        agent="analyzer",
        status="completed",
        started_at=analyzer_start,
        metadata={
            "incident_status": "incident_detected",
        },
    )

    decision_start = start_timer()
    time.sleep(0.01)

    observer.record_agent(
        agent="decision",
        status="completed",
        started_at=decision_start,
        metadata={
            "severity": "critical",
            "decision": "request_remediation",
        },
    )

    result = observer.summary()

    print("\n=== AGENTIC DEVOPS OBSERVABILITY ===")

    for key, value in result.items():
        print(f"{key}: {value}")