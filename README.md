### My First MCP Server (Portfolio Manager) and Client.

## Prerequisites
1. Install uv package manager
2. Download and Install Claude Desktop - https://claude.ai/download
3. (Optional) Install Claude Code - `npm install -g @anthropic-ai/claude-code`


### Create Virtual Env

```Shell
# deprecated pip and migrated to use uv
#python3 -m venv .venv
uv venv
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
uv run mcp install ./my-mcp-server/main.py
or
mcp install ./my-mcp-server/main.py
```

### Debug MCP Server
```Shell
# debug MCP server
mcp dev ./my-mcp-server/main.py
or
npx @modelcontextprotocol/inspector uv run ./my-mcp-server/main.py
```

### Custom MCP Client
This custom MCP Client Uses OpenAI APIs for Chat Completions. 
We are using Sampling Handler to Request the client’s LLM to generate text based on provided messages. This is useful when the function needs to leverage the LLM’s capabilities to process data or generate responses.

**Note:** Create `.env` file in the project and add `OPENAI_API_KEY=<add your key>`

### Run MCP Client
```Shell
uv run ./my-mcp-client.py/client.py
```
