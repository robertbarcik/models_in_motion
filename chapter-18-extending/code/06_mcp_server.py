"""A minimal MCP server: our churn scorer, exposed in the standard
grammar so ANY MCP client can discover and call it. Speaks over stdio."""

import json

from mcp.server.mcpserver import MCPServer

server = MCPServer("churn-model")

SCORES = {"C-1001": 0.82, "C-1002": 0.11}       # stand-in for the Part 1
                                                # Flask /predict service


@server.tool()
def get_churn_risk(customer_id: str) -> str:
    """Return the churn risk score (0-1) for a customer, from our
    deployed churn model. customer_id looks like C-1001."""
    return json.dumps({"customer_id": customer_id,
                       "churn_risk": SCORES.get(customer_id, 0.5)})


@server.resource("churn://model-card")
def model_card() -> str:
    """What this model is and how to read its score."""
    return ("Churn model v3, gradient boosting, trained 2026-06. Score is "
            "P(churn within 90 days). Above 0.7 = call the customer.")


if __name__ == "__main__":
    server.run(transport="stdio")
