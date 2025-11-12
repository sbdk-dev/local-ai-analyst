# Semantic Layer Documentation Map

Quick reference guide for semantic-layer documentation - "What to read when"

## Getting Started

| Need | Read This | Purpose |
|------|-----------|---------|
| **Set up and run** | [README.md](./README.md) | Overview and quick start |
| **Understand the system** | [/CLAUDE.md](../CLAUDE.md) | Complete architecture and design |
| **Learn concepts** | [SEMANTIC_MODEL_DOCUMENTATION.md](./SEMANTIC_MODEL_DOCUMENTATION.md) | Semantic model design guide |
| **Deploy to Claude Desktop** | [/QUICK_START.md](../QUICK_START.md) | Setup and configuration |

## Understanding Components

### Semantic Layer & Models
- **[SEMANTIC_MODEL_DOCUMENTATION.md](./SEMANTIC_MODEL_DOCUMENTATION.md)** - Semantic model design and usage
- **[SEMANTIC_MODEL_DECISIONS.md](./SEMANTIC_MODEL_DECISIONS.md)** - Design decisions and rationale
- **[models/](./models/)** - Actual model YAML files

### MCP Server
- **[mcp_server/](./mcp_server/)** - FastMCP server implementation
- **[mcp_server/server.py](./mcp_server/server.py)** - Main server file with 22 tools
- **[mcp_server/tools.py](./mcp_server/tools.py)** - Tool definitions
- **[mcp_server/intelligence.py](./mcp_server/intelligence.py)** - Intelligence layer

### Performance & Optimization
- **[PERFORMANCE_SUMMARY.md](./PERFORMANCE_SUMMARY.md)** - Performance metrics and optimization results

### Design & Architecture
- **[DESIGN_NOTES.md](./DESIGN_NOTES.md)** - Design decisions and notes
- **[docs/](./docs/)** - Additional documentation

## Testing

| Test File | Tests What |
|-----------|-----------|
| [test_all_functionality.py](./test_all_functionality.py) | Complete system integration |
| [test_semantic_layer_fix.py](./test_semantic_layer_fix.py) | Semantic layer functionality |
| [test_workflow_orchestrator_fix.py](./test_workflow_orchestrator_fix.py) | Workflow orchestration |
| [test_intelligence_engine_fix.py](./test_intelligence_engine_fix.py) | Intelligence layer |
| [test_tdd_memory_and_stats.py](./test_tdd_memory_and_stats.py) | Memory and statistics |

Run all tests:
```bash
uv run pytest test_all_functionality.py -v
```

## Running the System

```bash
# Start the MCP server
uv run python run_mcp_server.py

# Run all tests
uv run python test_all_functionality.py

# Run specific tests
uv run pytest test_semantic_layer_fix.py -v
```

## Key Files at a Glance

### Configuration
- `pyproject.toml` - Project dependencies and configuration
- `claude_desktop_config.json` - Claude Desktop MCP configuration
- `.python-version` - Python version specification

### Data
- `data/analytics.duckdb` - DuckDB analytics database
- `generate_sample_data.py` - Sample data generation script
- `load_to_duckdb.py` - Database loading script

### Models
- `models/customers.yml` - Customer metrics and dimensions
- `models/orders.yml` - Order analytics
- `models/revenue.yml` - Revenue metrics

### Server
- `run_mcp_server.py` - Entry point to start MCP server
- `mcp_server/server.py` - FastMCP server implementation
- `mcp_server/tools.py` - 22 MCP tools implementation
- `mcp_server/intelligence.py` - Statistical testing and NLG

## Directory Structure

```
semantic-layer/
├── README.md                           # Start here
├── DOCUMENTATION_MAP.md               # This file
├── SEMANTIC_MODEL_DOCUMENTATION.md    # Model design guide
├── SEMANTIC_MODEL_DECISIONS.md        # Design decisions
├── DESIGN_NOTES.md                    # Architecture notes
├── PERFORMANCE_SUMMARY.md             # Performance metrics
├── models/                            # Semantic models (YAML)
│   ├── customers.yml
│   ├── orders.yml
│   └── revenue.yml
├── mcp_server/                        # FastMCP server
│   ├── server.py
│   ├── tools.py
│   └── intelligence.py
├── data/                              # DuckDB database
│   └── analytics.duckdb
├── docs/                              # Additional documentation
├── tests/                             # Pytest fixtures and helpers
├── examples/                          # Example usage
├── archive/                           # Archived documentation
│   └── old-docs/
│       └── README.md                  # Archive explanation
└── [test files].py                    # Individual test suites
```

## Status and Quality

**Current Status**: ✅ Production Ready (100% Complete)
- **Tests**: 7/7 passing (100% pass rate)
- **Components**: All 7 major components functional
- **MCP Tools**: 22 tools operational
- **Documentation**: Comprehensive and up-to-date

For complete status: See [.hive-mind/FINAL_STATUS_REPORT.md](../.hive-mind/FINAL_STATUS_REPORT.md)

## Need More Detail?

### Architecture Deep Dive
→ See `/CLAUDE.md` (complete system architecture)

### Semantic Layer Design
→ See [SEMANTIC_MODEL_DOCUMENTATION.md](./SEMANTIC_MODEL_DOCUMENTATION.md)

### How the MCP Tools Work
→ See `mcp_server/tools.py` and individual tool docstrings

### Test Details
→ See the specific test file for that component

### Historical Context
→ See `archive/old-docs/README.md` or `.hive-mind/` for historical documents

---

**Last Updated**: November 11, 2025
**Status**: Production Ready
**Project**: AI Analyst System with Semantic Layer Integration
