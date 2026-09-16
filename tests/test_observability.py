"""Tests for Agentic DevOps workflow observability."""

from src.agent.observability import WorkflowObserver, start_timer


def test_observer_records_agent_trace():
    observer = WorkflowObserver()

    started_at = start_timer()

    observer.record_agent(
        agent="analyzer",
        status="completed",
        started_at=started_at,
        metadata={"incident_status": "incident_detected"},
    )

    summary = observer.summary()

    assert summary["agent_count"] == 1
    assert summary["completed_agents"] == 1
    assert summary["failed_agents"] == 0

    trace = summary["traces"][0]

    assert trace["agent"] == "analyzer"
    assert trace["status"] == "completed"
    assert trace["duration_ms"] >= 0
    assert trace["metadata"]["incident_status"] == "incident_detected"


def test_observer_counts_failed_agents():
    observer = WorkflowObserver()

    started_at = start_timer()

    observer.record_agent(
        agent="llm_reasoning",
        status="failed",
        started_at=started_at,
        metadata={"error": "LLM unavailable"},
    )

    summary = observer.summary()

    assert summary["agent_count"] == 1
    assert summary["completed_agents"] == 0
    assert summary["failed_agents"] == 1


def test_observer_generates_workflow_summary():
    observer = WorkflowObserver()

    analyzer_start = start_timer()
    observer.record_agent(
        agent="analyzer",
        status="completed",
        started_at=analyzer_start,
    )

    decision_start = start_timer()
    observer.record_agent(
        agent="decision",
        status="completed",
        started_at=decision_start,
    )

    summary = observer.summary()

    assert summary["workflow_id"]
    assert summary["total_duration_ms"] >= 0
    assert summary["agent_count"] == 2
    assert summary["completed_agents"] == 2
    assert summary["failed_agents"] == 0
    assert len(summary["traces"]) == 2