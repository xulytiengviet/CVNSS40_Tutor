# ChatGPT companion skill for CVNSS4.0 Knowledge Hub

This folder is an **optional skills-only plugin source package** following Agent Plugins 1.0. The companion skill teaches an AI when to use the CVNSS4.0 Oracle and how to handle ambiguity, provenance, quizzes and training. It **does not create or host an MCP server** and does not by itself make the converter callable from ChatGPT.

To use live tools in ChatGPT:
1. Read [full setup guide](../../cvnss_hub/CHATGPT_PLUGIN.md).
2. Start the MCP server, verify via MCP Inspector and expose via verified HTTPS or Secure MCP Tunnel.
3. In ChatGPT, register the remote MCP as a plugin using **Add custom MCP server**.
4. When packaging this companion skill with the existing MCP plugin, retain its verified server binding. Do not invent an `mcp.json` URL, and do not re-register a second duplicate server.

This directory intentionally omits `mcp.json` until a real endpoint has been deployed. It is a reusable instruction layer, not proof of a working cloud connection.
