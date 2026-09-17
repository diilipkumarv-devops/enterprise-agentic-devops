from src.agent.evaluation import WorkflowEvaluator


def build_safe_workflow():
    """Create a safe critical-incident workflow for testing."""

    return {
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
            "workflow_id": "test-workflow-001",
            "failed_agents": 0,
        },
    }


def test_safe_workflow_passes_evaluation():
    evaluator = WorkflowEvaluator()

    result = evaluator.evaluate(
        build_safe_workflow()
    )

    assert result["evaluation_status"] == "passed"
    assert result["quality_score"] == 1.0
    assert result["safe_execution"] is True

    assert all(
        result["checks"].values()
    )


def test_low_llm_confidence_fails_evaluation():
    evaluator = WorkflowEvaluator()

    workflow = build_safe_workflow()

    workflow["llm_reasoning_agent"]["reasoning"][
        "confidence"
    ] = 0.40

    result = evaluator.evaluate(workflow)

    assert result["evaluation_status"] == "failed"

    assert (
        result["checks"][
            "llm_confidence_acceptable"
        ]
        is False
    )

    assert result["quality_score"] < 1.0


def test_guardrail_failure_fails_evaluation():
    evaluator = WorkflowEvaluator()

    workflow = build_safe_workflow()

    workflow["guardrails"][
        "guardrail_status"
    ] = "blocked"

    result = evaluator.evaluate(workflow)

    assert result["evaluation_status"] == "failed"

    assert (
        result["checks"]["guardrails_passed"]
        is False
    )


def test_agent_failure_fails_evaluation():
    evaluator = WorkflowEvaluator()

    workflow = build_safe_workflow()

    workflow["observability"][
        "failed_agents"
    ] = 1

    result = evaluator.evaluate(workflow)

    assert result["evaluation_status"] == "failed"

    assert (
        result["checks"]["no_agent_failures"]
        is False
    )


def test_critical_action_without_approval_fails():
    evaluator = WorkflowEvaluator()

    workflow = build_safe_workflow()

    workflow["decision_agent"]["decision"][
        "requires_human_approval"
    ] = False

    result = evaluator.evaluate(workflow)

    assert result["evaluation_status"] == "failed"

    assert (
        result["checks"][
            "critical_action_requires_approval"
        ]
        is False
    )


def test_audit_record_contains_workflow_data():
    evaluator = WorkflowEvaluator()

    result = evaluator.evaluate(
        build_safe_workflow()
    )

    audit = result["audit_record"]

    assert audit["workflow_id"] == "test-workflow-001"
    assert audit["severity"] == "critical"
    assert audit["decision"] == "request_remediation"
    assert audit["llm_confidence"] == 0.80
    assert audit["guardrail_status"] == "passed"
    assert audit["human_approval_required"] is True
    assert audit["execution_status"] == "blocked"
    assert audit["failed_agents"] == 0
    assert audit["timestamp_utc"] is not None