import os
import sys
from fastmcp import FastMCP

# Initialize a dummy FastMCP context block to safely utilize its auto-diagramming layer
mcp = FastMCP("enterprise-devops-broker")

@mcp.tool()
def generate_portfolio_map() -> str:
    """
    Renders the platform connectivity blueprint matrix.
    Tracks structural flows across n8n, custom MCP brokers, and multi-cloud AKS/EKS targets.
    """
    diagram_flow = (
        "┌────────────────────────────────────────────────────────┐\n"
        "│      ENTERPRISE AGENTIC DEVOPS PLATFORM ARCHITECTURE    │\n"
        "└────────────────────────────────────────────────────────┘\n"
        "                           │\n"
        "                           ▼ [SRE Incident Metrics Alerts / Webhooks]\n"
        "┌────────────────────────────────────────────────────────┐\n"
        "│         LOCAL DOCKER PLANE CONTROL RUNTIME HUB         │\n"
        "│  ├── n8n Orchestrator Engine (Multi-Agent Workflow)     │\n"
        "│  ├── Prometheus Engine (Metrics Scraper Pipeline)      │\n"
        "│  └── Grafana Dashboard System (Telemetry Analytics Dashboard) │\n"
        "└────────────────────────────────────────────────────────┘\n"
        "                           │\n"
        "                           ▼ [Standard I/O Secure Streams]\n"
        "┌────────────────────────────────────────────────────────┐\n"
        "│             CUSTOM PYTHON DEVOPS MCP CORE              │\n"
        "│   ├── tool: inspect_system_health()                    │\n"
        "│   └── tool: fetch_incident_logs()                       │\n"
        "└────────────────────────────────────────────────────────┘\n"
        "                           │\n"
        "              ┌────────────┴────────────┐\n"
        "              ▼                         ▼\n"
        "┌───────────────────────────┐ ┌───────────────────────────┐\n"
        "│  MICROSOFT AZURE DOMAIN   │ │    AMAZON WEB SERVICES    │\n"
        "│  └── Managed AKS Cluster  │ │  └── Managed EKS Cluster │\n"
        "│      (Private CNI VNet)   │ │      (Private IRSA VPC)   │\n"
        "└───────────────────────────┘ └───────────────────────────┘\n"
    )
    return diagram_flow

if __name__ == "__main__":
    # Natively writes out your structured text layout map directly into your documentation directory
    print(generate_portfolio_map())
    with open("architecture_map.txt", "w", encoding="utf-8") as f:
        f.write(generate_portfolio_map())
    print("\n[SUCCESS] System architecture blueprint map generated cleanly inside documentation/architecture_map.txt!")
