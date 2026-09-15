"""MCP client for the Enterprise Agentic DevOps platform."""

from pathlib import Path

from fastmcp import Client


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MCP_SERVER_PATH = PROJECT_ROOT / "mcp-servers" / "devops_server.py"

##MCP_SERVER_PATH = "mcp-servers/devops_server.py"


async def get_system_health() -> str:
    """Call the MCP health tool and return its text result."""

    client = Client(MCP_SERVER_PATH)

    async with client:
        result = await client.call_tool(
            "inspect_system_health",
            {},
        )

    return result.data


async def get_incident_logs(pod_name: str) -> str:
    """Call the MCP log tool for a specific Kubernetes pod."""

    client = Client(MCP_SERVER_PATH)

    async with client:
        result = await client.call_tool(
            "fetch_incident_logs",
            {
                "pod_name": pod_name,
            },
        )

    return result.data
async def run_mcp_diagnostics() -> None:
    """Run the complete MCP diagnostic sequence."""

    health_report = await get_system_health()

    print("=== MCP HEALTH RESULT ===")
    print(health_report)

    logs = await get_incident_logs(
        "payment-gateway-processor-x92"
    )

    print("\n=== MCP LOG RESULT ===")
    print(logs)
if __name__ == "__main__":
    import asyncio

    asyncio.run(run_mcp_diagnostics())