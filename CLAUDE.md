# AI Analyst System - Semantic Layer Integration

## Project Overview

**Goal**: Build a semantic layer-powered AI analyst that connects to Claude Desktop and ChatGPT Desktop via MCP (Model Context Protocol), enabling natural language data analysis with statistical rigor and incremental exploration.

**Status**: v1.0 Production Ready | 100% Test Pass Rate | 23 MCP Tools

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│        Claude Desktop / ChatGPT Desktop                 │
└────────────────────┬────────────────────────────────────┘
                     │ MCP Protocol (23 Tools)
┌────────────────────▼────────────────────────────────────┐
│              FastMCP Server                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Multi-Query Workflow Engine             │   │
│  │  • Dependency Resolution & Parallel Execution   │   │
│  │  • 3 Built-in Analytical Workflows              │   │
│  └─────────────────┬───────────────────────────────┘   │
│                    │                                    │
│  ┌─────────────────▼───────────────────────────────┐   │
│  │         Query Optimization Engine               │   │
│  │  • Intelligent Caching (95% hit rate)          │   │
│  │  • Performance Learning                        │   │
│  └─────────────────┬───────────────────────────────┘   │
│                    │                                    │
│  ┌─────────────────▼───────────────────────────────┐   │
│  │         Conversation Memory                     │   │
│  │  • 24-hour Context Window                      │   │
│  │  • Pattern Recognition                         │   │
│  └─────────────────┬───────────────────────────────┘   │
│                    │                                    │
│  ┌─────────────────▼───────────────────────────────┐   │
│  │         Intelligence Layer                      │   │
│  │  • Statistical Testing                         │   │
│  │  • Natural Language Generation                 │   │
│  └─────────────────┬───────────────────────────────┘   │
│                    │                                    │
│  ┌─────────────────▼───────────────────────────────┐   │
│  │         Semantic Layer (Ibis + DuckDB)         │   │
│  │  • Product Analytics Models                    │   │
│  │  • Business Logic & Metrics                    │   │
│  └─────────────────┬───────────────────────────────┘   │
└────────────────────┼────────────────────────────────────┘
                     │
               ┌─────▼──────┐
               │   DuckDB   │
               └────────────┘
```

---

## Core Principles

### 1. Execution-First (Prevent Fabrication)

**Pattern**: Build → Execute → Annotate

```python
# NEVER generate observations without running queries
query = builder.generate_query(question)
result = executor.run(query)  # MUST execute first
interpretation = interpret(result)  # Based on REAL data
```

### 2. Incremental Exploration

**Pattern**: One Question Per Turn

```python
# Start simple
"How many customers do we have?"
→ SELECT COUNT(*) FROM customers

# Build complexity based on results
"What's the breakdown by industry?"
→ SELECT industry, COUNT(*) FROM customers GROUP BY industry
```

### 3. Statistical Rigor by Default

Auto-run tests when comparing groups:
- Chi-square or t-test for group comparisons
- Confidence intervals for correlations
- Sample size validation for claims

### 4. Natural Language Communication

**Concise observations**:
- "Tech customers 2x higher LTV" ✅
- NOT: "Upon analyzing the data, Technology segment customers demonstrate..." ❌

---

## Quick Start

### Environment Setup

```bash
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/sbdk-dev/claude-analyst.git
cd claude-analyst/semantic-layer
uv sync

# Test the system
uv run python test_all_functionality.py
```

### Claude Desktop Integration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ai-analyst": {
      "command": "/opt/homebrew/bin/uv",
      "args": ["run", "python", "run_mcp_server.py"],
      "cwd": "/path/to/claude-analyst/semantic-layer"
    }
  }
}
```

**Note**: Use full path to `uv` (find with `which uv`). GUI apps don't inherit shell PATH.

### ChatGPT Desktop Integration

```bash
# 1. Set OpenAI API key
export OPENAI_API_KEY="sk-your-key-here"

# 2. Start the OpenAI API server
cd semantic-layer
uv run python run_openai_server.py
# Server starts on http://localhost:8000

# 3. Configure ChatGPT Desktop
# Settings → Beta Features → Actions → Add Custom Action
# URL: http://localhost:8000
```

---

## File Structure

```
claude-analyst/
├── CLAUDE.md                    # This file
├── README.md                    # Quick start and overview
├── QUICK_START.md               # Detailed setup guide
├── LICENSE                      # MIT License
├── semantic-layer/              # Main implementation
│   ├── models/                  # Semantic models (YAML)
│   │   ├── users.yml
│   │   ├── events.yml
│   │   └── engagement.yml
│   ├── mcp_server/              # FastMCP server
│   │   ├── server.py
│   │   ├── tools.py
│   │   └── intelligence_layer.py
│   ├── data/                    # DuckDB database
│   │   └── analytics.duckdb
│   ├── run_mcp_server.py        # Server entry point
│   ├── run_openai_server.py     # ChatGPT integration
│   └── test_all_functionality.py
└── scripts/
    └── setup.sh
```

---

## MCP Tools

### Core Tools

| Tool | Description |
|------|-------------|
| `list_models` | List available semantic models |
| `query_model` | Execute queries against semantic layer |
| `suggest_analysis` | Get context-aware next questions |
| `test_significance` | Run statistical tests |

### Workflow Tools

| Tool | Description |
|------|-------------|
| `run_workflow` | Execute multi-step analytical workflows |
| `list_workflows` | List available workflow templates |
| `get_workflow_status` | Check workflow execution status |

### Memory Tools

| Tool | Description |
|------|-------------|
| `get_context` | Retrieve conversation context |
| `get_suggestions` | Get analysis suggestions based on history |

### Optimization Tools

| Tool | Description |
|------|-------------|
| `get_cache_stats` | View query cache statistics |
| `optimize_query` | Get query optimization recommendations |

---

## Semantic Model Design

Following [Rasmus Engelbrecht's patterns](https://rasmusengelbrecht.substack.com/p/practical-guide-to-semantic-layers):

1. **Start with the business question, not the schema**
2. **Metrics should be self-contained and reusable**
3. **Dimensions define how metrics can be sliced**
4. **Keep models simple and composable**

### Example Model

```yaml
model:
  name: users
  description: "User metrics and dimensions"

dimensions:
  - name: user_id
    type: string
    primary_key: true
  - name: plan_type
    type: string
    description: "Subscription plan"
  - name: industry
    type: string

measures:
  - name: total_users
    type: count_distinct
    field: user_id
  - name: conversion_rate
    type: ratio
    numerator: converted_users
    denominator: total_users
```

---

## Performance Metrics

- **23 MCP Tools**: All functional and tested
- **Test Pass Rate**: 100% (7/7 tests)
- **Cache Hit Rate**: 95% for repeated queries
- **Query Response Time**: <100ms for cached queries
- **Workflow Templates**: 3 (conversion, feature, revenue)

---

## Technology Stack

- **MCP Server**: [FastMCP](https://github.com/jlowin/fastmcp)
- **Semantic Layer**: [Boring Semantic Layer](https://github.com/boring-opensource/boring-semantic-layer)
- **Query Engine**: [Ibis](https://ibis-project.org/)
- **Database**: [DuckDB](https://duckdb.org/)
- **Statistical Testing**: scipy

---

## References

- [Rasmus: Practical Guide to Semantic Layers](https://rasmusengelbrecht.substack.com/p/practical-guide-to-semantic-layers)
- [Boring Semantic Layer Documentation](https://github.com/boring-opensource/boring-semantic-layer)
- [Ibis Documentation](https://ibis-project.org/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [Model Context Protocol Spec](https://modelcontextprotocol.io/)

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

**Version**: 1.0
**Last Updated**: November 2025
**Author**: Matt Strautmann
