# Claude Desktop Integration Setup

This guide shows how to connect the AI Analyst MCP server to Claude Desktop.

## Prerequisites

- Claude Desktop app installed
- AI Analyst MCP server working locally (test with `uv run python test_mcp_server.py`)

## Setup Steps

### 1. Locate Claude Desktop Config

Find your Claude Desktop configuration file:

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

### 2. Find Full Path to UV

GUI apps don't inherit shell PATH, so you need the full path to `uv`:

```bash
which uv
# Common locations:
# macOS (Homebrew): /opt/homebrew/bin/uv
# macOS (curl install): ~/.cargo/bin/uv
# Linux: ~/.cargo/bin/uv
```

### 3. Add AI Analyst MCP Server

Open the configuration file and add our server to the `mcpServers` section:

```json
{
  "mcpServers": {
    "ai-analyst": {
      "command": "/opt/homebrew/bin/uv",
      "args": [
        "run",
        "python",
        "run_mcp_server.py"
      ],
      "cwd": "/path/to/claude-analyst/semantic-layer"
    }
  }
}
```

**Important:**
- Update the `command` path to your actual `uv` location (from `which uv`)
- Update the `cwd` path to match your actual installation directory

### 4. Test Configuration

Copy the configuration from `claude_desktop_config.json` in this directory:

```bash
cp claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

Or merge it with your existing configuration if you have other MCP servers.

### 5. Restart Claude Desktop

1. Quit Claude Desktop completely
2. Restart the application
3. The AI Analyst tools should now be available

## Available Tools

Once connected, you'll have access to these MCP tools:

### Core Analysis Tools

- **`list_models`** - List available semantic models (users, events, engagement)
- **`get_model`** - Get detailed schema for a specific model
- **`query_model`** - Query data with execution-first pattern and statistical analysis
- **`suggest_analysis`** - Get suggestions for next analysis steps
- **`test_significance`** - Run statistical significance tests

### System Tools

- **`health_check`** - Check system health and database connection
- **`get_sample_queries`** - Get example queries for a model

## Example Usage

Once connected, try these commands in Claude Desktop:

```
List available models

What's our conversion rate by plan type?

Show me the most popular features

How does engagement vary by industry?

Test if the difference in engagement by plan type is statistically significant
```

## Architecture

The integration follows this flow:

```
Claude Desktop → MCP Protocol → AI Analyst Server → Semantic Layer → DuckDB
```

### Execution-First Pattern

The system implements **Build → Execute → Annotate** to prevent fabrication:

1. **Build**: Generate SQL query from semantic model
2. **Execute**: Run query against real database
3. **Annotate**: Generate interpretation based on actual results

### Statistical Rigor

- Auto-validates sample sizes
- Runs significance tests when comparing groups
- Calculates effect sizes
- Provides business context with benchmarks

### Natural Language

- Concise observations ("Tech 2x higher LTV")
- Shows statistical evidence (p-values, sample sizes)
- Suggests logical next questions
- Includes business benchmarks

## Troubleshooting

### MCP Server Not Starting

1. Test locally first:
   ```bash
   cd /path/to/claude-analyst/semantic-layer
   uv run python test_mcp_server.py
   ```

2. Check the path in the config file matches your installation

3. Ensure the virtual environment exists:
   ```bash
   ls .venv/
   ```

### Tools Not Appearing

1. Restart Claude Desktop completely
2. Check the configuration file syntax (valid JSON)
3. Look for error messages in Claude Desktop

### Query Errors

1. Verify database exists:
   ```bash
   ls data/analytics.duckdb
   ```

2. Test semantic models:
   ```bash
   ls models/*.yml
   ```

3. Run the test script to check all components

## Advanced Configuration

### Different Database

To use a different database, update the semantic layer configuration:

1. Edit `mcp_server/semantic_layer_integration.py`
2. Change the database path in line 25:
   ```python
   self.db_path = Path("path/to/your/database.duckdb")
   ```

### Custom Semantic Models

Add new semantic models:

1. Create `.yml` files in the `models/` directory
2. Follow the existing model patterns
3. Restart the MCP server

### Production Deployment

For production use:

1. Use a production database (PostgreSQL, Snowflake, etc.)
2. Configure authentication and security
3. Add monitoring and logging
4. Set up proper error handling

## Support

If you encounter issues:

1. Check the test script passes: `uv run python test_mcp_server.py`
2. Verify Claude Desktop configuration syntax
3. Look for error messages in Claude Desktop
4. Check the semantic model definitions in `models/`

The AI Analyst follows Mercury project learnings and Rasmus Engelbrecht's semantic layer patterns for reliable, statistical analysis.