> **Trạng thái vận hành 30/10/2026:** Render đã báo `Live` cho dịch vụ [cvnss40-mcp](https://dashboard.render.com/web/srv-dbi1sj1srm7s73d0tnb0) tại `https://cvnss40-mcp.onrender.com/mcp`. Plugin cá nhân CVNSS4.0 Knowledge Hub v0.1.0 đã được **tạo riêng trong ChatGPT** và có `mcp.json` trỏ đến URL đó. Cần **cài plugin/cho phép sử dụng** trong giao diện ChatGPT và chạy thử một lệnh `cvnss_convert` mới xác nhận được kết nối đầu cuối. Render đang tự triển khai theo `commit`, chưa phải `checksPass`. Gói MCP công khai chỉ đọc, không OAuth, không đồng bộ hồ sơ riêng/RAG.

# ChatGPT companion skill for CVNSS4.0 Knowledge Hub

## Source update 0.2.0

Version 0.2.0 adds ten knowledge topics, evidence/review labels and guidance for
learners, teachers, developers and researchers. Built ZIPs include offline
`references/knowledge.json`, `knowledge.schema.json` and `standardization.md`
inside the skill, copied from canonical files in `cvnss_hub/`.
Connected servers from this source also expose `cvnss_knowledge`; older servers
may not. These are draft editorial materials, not a completed official standard.
Building this version does not update the separately installed ChatGPT plugin or
deploy a new Render server. Update the existing plugin binding/package rather
than creating duplicate servers. The operational note above describes the earlier
0.1.0 installation, not deployment of this source update.

This folder is an **optional skills-only plugin source package** following Agent Plugins 1.0. The companion skill teaches an AI when to use the CVNSS4.0 Oracle and how to handle ambiguity, provenance, quizzes and training. It **does not create or host an MCP server** and does not by itself make the converter callable from ChatGPT.

To use live tools in ChatGPT:
1. Read [full setup guide](../../cvnss_hub/CHATGPT_PLUGIN.md).
2. Start the MCP server, verify via MCP Inspector and expose via verified HTTPS or Secure MCP Tunnel.
3. In ChatGPT, register the remote MCP as a plugin using **Add custom MCP server**.
4. When packaging this companion skill with the existing MCP plugin, retain its verified server binding. Do not invent an `mcp.json` URL, and do not re-register a second duplicate server.

The repository intentionally omits a hardcoded `mcp.json`: run the builder with `--mcp-url https://cvnss40-mcp.onrender.com/mcp` to include the verified Render-hosted URL. A private ChatGPT plugin v0.1.0 was created separately and is not installed by committing this repository. User installation and a real MCP tool call remain necessary.

## Reproducible ZIP package

From repository root on Windows, run `py scripts/build_cvnss_chatgpt_plugin.py`.
It creates `dist/cvnss4-knowledge-hub-0.2.0.zip` (skills-only). The focused GitHub Actions workflow uploads this same ZIP as a build artifact.

After deploying **and testing** an authenticated HTTPS MCP server, run
`py scripts/build_cvnss_chatgpt_plugin.py --mcp-url https://cvnss40-mcp.onrender.com/mcp`
to include a portable `mcp.json` pointing at that URL.

For GitHub auto-deploy, ChatGPT metadata refreshing and differences between code,
RAG and memory sync, see [GITHUB_SYNC.md](GITHUB_SYNC.md).
