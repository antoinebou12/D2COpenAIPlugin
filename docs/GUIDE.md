# ChatGPT setup

For a Custom GPT, import the deployed `/openapi.json` schema into an Action and select no authentication. The existing `generate_diagram_endpoint` operation accepts `lang`, `type`, `code`, and an optional `theme`.

For an MCP app, connect to the deployed `/mcp/` endpoint. Test initialization and `tools/list`, then call `generate_diagram` with the same arguments.

See [README](../README.md) for local commands, backend configuration, deployment settings and examples. The old plugin-store installation workflow is no longer the setup path for this version.
