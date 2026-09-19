"""LLM reasoning layer for the Enterprise Agentic DevOps platform."""

from __future__ import annotations
import os
import json
import urllib.error
import urllib.request


class LLMReasoningService:
    """
    Generate structured incident reasoning using a local Ollama model.

    The LLM provides advisory reasoning only.
    It does not authorize or execute remediation actions.
    """

    def __init__(
        self,
        #model: str = "llama3.2",
        model: str = "llama3.2:3b",
        base_url: str | None = None,
        timeout: int = 60,
    ) -> None:
        self.model = model
        self.base_url = base_url or os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434",
     )
        self.timeout = timeout

    def build_prompt(self, incident: dict) -> str:
        """Build a constrained prompt from structured incident evidence."""

        return f"""
You are an enterprise DevOps/SRE incident reasoning assistant.

Analyze the incident evidence below.

INCIDENT:
Status: {incident.get("status", "unknown")}
Pod: {incident.get("pod", "unknown")}
Root cause: {incident.get("root_cause", "unknown")}
Recommendation: {incident.get("recommendation", "unknown")}

Return ONLY valid JSON using exactly this structure:

{{
  "diagnosis": "short technical diagnosis",
  "reasoning_summary": "short explanation based only on the evidence",
  "recommended_action": "safe recommended next action",
  "confidence": 0.0
}}

Rules:
- confidence must be between 0.0 and 1.0.
- Do not claim that remediation was executed.
- Do not authorize production changes.
- Do not invent infrastructure evidence.
- Credential changes require human approval.
""".strip()

    def reason(self, incident: dict) -> dict:
        """Call local Ollama and return structured LLM reasoning."""

        prompt = self.build_prompt(incident)

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }

        request_data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            url=f"{self.base_url}/api/generate",
            data=request_data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
            ) as response:
                response_body = response.read().decode("utf-8")

        except urllib.error.URLError as exc:
            return {
                "status": "unavailable",
                "diagnosis": "LLM reasoning service is unavailable.",
                "reasoning_summary": str(exc),
                "recommended_action": (
                    "Continue using deterministic incident policy."
                ),
                "confidence": 0.0,
            }

        ollama_result = json.loads(response_body)
        generated_text = ollama_result.get("response", "{}")

        try:
            reasoning = json.loads(generated_text)

        except json.JSONDecodeError:
            return {
                "status": "invalid_response",
                "diagnosis": "LLM returned an invalid structured response.",
                "reasoning_summary": generated_text,
                "recommended_action": (
                    "Continue using deterministic incident policy."
                ),
                "confidence": 0.0,
            }

        return {
            "status": "completed",
            "diagnosis": reasoning.get(
                "diagnosis",
                "No diagnosis provided.",
            ),
            "reasoning_summary": reasoning.get(
                "reasoning_summary",
                "No reasoning summary provided.",
            ),
            "recommended_action": reasoning.get(
                "recommended_action",
                "No action recommended.",
            ),
            "confidence": reasoning.get(
                "confidence",
                0.0,
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
        "recommendation": (
            "Validate the database credentials and secret configuration. "
            "Do not automatically rotate or modify production credentials "
            "without human approval."
        ),
    }

    service = LLMReasoningService()

    result = service.reason(example_incident)

    print("\n=== LLM INCIDENT REASONING ===")

    for key, value in result.items():
        print(f"{key}: {value}")