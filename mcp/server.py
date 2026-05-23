from mcp.server.fastmcp import FastMCP
import json
import requests

# Create an MCP server
mcp = FastMCP("model-api-mcp")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def PredictSleep(age: int, sleep: float) -> str:
    """
    Predicts whether a person will have sleep problems or not.

    Args:
        age: person's age in years (e.g. 32)
        sleep: sleep duration in hours (e.g. 6.1)

    Returns:
        JSON string with prediction: 1 (sleep problem) or 0 (no sleep problem)
    """
    response = requests.post(url="http://127.0.0.1:8000",
                             headers={"Accept": "application/json", "Content-Type": "application/json"},
                             data=json.dumps({"age": age, "sleep": sleep}))

    return json.dumps(response.json())


if __name__ == "__main__":
    mcp.run(transport="stdio")