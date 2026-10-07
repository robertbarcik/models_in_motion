"""No SDK on the client side: talk to the MCP server with raw JSON-RPC
lines over its stdin/stdout, to see there is no magic in the socket."""

import json
import subprocess
import sys

p = subprocess.Popen([sys.executable, "06_mcp_server.py"],
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     text=True)


def send(msg):
    p.stdin.write(json.dumps(msg) + "\n")
    p.stdin.flush()
    if "id" in msg:                       # requests get replies,
        return json.loads(p.stdout.readline())   # notifications don't


send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
      "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                 "clientInfo": {"name": "raw", "version": "0"}}})
send({"jsonrpc": "2.0", "method": "notifications/initialized"})

reply = send({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
              "params": {"name": "get_churn_risk",
                         "arguments": {"customer_id": "C-1002"}}})
print(json.dumps(reply, indent=1)[:400])
p.terminate()
