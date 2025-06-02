### My First MCP Server - Portfolio Manager

## Prerequisites
1. Install uv package manager
2. Download and Install Claude Desktop - https://claude.ai/download
3. (Optional) Install Claude Code - `npm install -g @anthropic-ai/claude-code`


### Create Virtual Env

```Shell
# deprecated pip and migrated to use uv
#python3 -m venv .venv
vu venv
```

### Activate Virtual Env

```Shell
source .venv/bin/activate
```

#### Install requirements
```Shell
#python3 -m pip install -r requirements.txt
uv add -r requirements.txt
```

```Shell
# Sync dependencies
uv sync
```

### Run MCP and Install to Claude
```Shell
#This installs MCP Server defined in main.py to Claude Config.
uv run mcp install ./portfolio-mcp-server/main.py
or
mcp install ./portfolio-mcp-server/main.py
```

### Debug MCP Server
```Shell
# debug MCP server
mcp dev ./portfolio-mcp-server/main.py
or
npx @modelcontextprotocol/inspector uv run ./portfolio-mcp-server/main.py
```