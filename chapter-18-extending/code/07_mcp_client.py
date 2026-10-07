"""A tiny MCP client: start the server as a subprocess, ask what it
offers, read a resource, call a tool. This is what a chat app or an
IDE does behind the scenes when you 'add an MCP server'."""

import asyncio
import sys

from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client

params = StdioServerParameters(command=sys.executable,
                               args=["06_mcp_server.py"])


async def main():
    async with Client(stdio_client(params)) as client:
        print("server:", client.server_info.name)

        tools = await client.list_tools()
        for t in tools.tools:
            print("tool:", t.name, "-", t.description.split(",")[0])
            print("      schema:", list(t.input_schema["properties"]))

        res = await client.list_resources()
        for r in res.resources:
            print("resource:", r.uri)
        card = await client.read_resource("churn://model-card")
        print("      ", card.contents[0].text[:60], "...")

        result = await client.call_tool("get_churn_risk",
                                        {"customer_id": "C-1001"})
        print("call_tool result:", result.content[0].text)


asyncio.run(main())
