# Claude Analyst - Semantic Layer AI Assistant

> Building an AI analyst that connects to Claude Desktop via MCP, enabling natural language data analysis with statistical rigor and incremental exploration.

## Quick Start

**Current Status**: Phase 1 Research Complete ✅ | Phase 2 Implementation Starting 🔄

### What is This?

An AI-powered data analyst that:
- Connects to Claude Desktop via Model Context Protocol (MCP)
- Queries a semantic layer (Boring Semantic Layer + Ibis)
- Provides statistically rigorous analysis with natural language
- Prevents fabrication through "Build → Execute → Annotate" workflow
- Explores data incrementally like a real data scientist

### Architecture

```
Claude Desktop → MCP Server → Semantic Layer → Ibis → DuckDB
                     ↓
              Intelligence Layer:
              - Incremental Query Builder
              - Auto Statistical Testing
              - Natural Language Generator
```

## Core Principles

1. **Execution-First**: Never generate observations without running queries first
2. **Incremental Exploration**: One question per turn, each result informs next
3. **Statistical Rigor by Default**: Auto-run significance tests on comparisons
4. **Natural Language**: "Tech 2x higher LTV" not "Upon analyzing the data..."

## Documentation

- **[CLAUDE.md](CLAUDE.md)** - Complete project documentation, roadmap, and technical details
- **[SEMANTIC_LAYER_RESEARCH.md](SEMANTIC_LAYER_RESEARCH.md)** - Research on semantic layers, Ibis, FastMCP
- **[DATA_SCIENCE_NOTEBOOK_STYLE_GUIDE.md](DATA_SCIENCE_NOTEBOOK_STYLE_GUIDE.md)** - Natural language patterns

## Inspiration

**Semantic Layer Design**: Based on [Rasmus Engelbrecht's practical guide to semantic layers](https://rasmusengelbrecht.substack.com/p/practical-guide-to-semantic-layers)

**Workflow Pattern**: Inspired by Mercury DS take-home analysis showing the importance of Build → Execute → Annotate to prevent fabrication

**Tech Stack**:
- [Boring Semantic Layer](https://github.com/boring-opensource/boring-semantic-layer) by Julien Hurault
- [Ibis](https://ibis-project.org/) for portable dataframes
- [FastMCP](https://github.com/jlowin/fastmcp) for MCP server
- [DuckDB](https://duckdb.org/) for local database

## Current Phase: Semantic Layer Setup

**Next Steps**:
1. Install: `uv pip install boring-semantic-layer ibis-framework[duckdb] fastmcp`
2. Create DuckDB database with sample data (following Rasmus's examples)
3. Define semantic models in YAML
4. Test local queries through Ibis

See [CLAUDE.md](CLAUDE.md) for detailed roadmap.

## Why This Matters

> "AI tools are getting incredibly good at handling tedious BI work. But instead of replacing data professionals, this shift frees us to focus on what drives value: designing strong data foundations, defining clear semantic layers, and partnering with stakeholders for real business impact."

This project demonstrates:
- How to build trustworthy AI analysts (execution-first prevents fabrication)
- Semantic layers as the foundation for self-service analytics
- MCP as the standard for AI-data integration
- Statistical rigor by default (not as an afterthought)

## Archive

Previous work archived in `archive/mercury-takehome/`:
- Mercury Data Science Manager take-home analysis
- Learnings documented and applied to this project

---

**Last Updated**: 2025-11-05
**License**: MIT
**Contact**: Matt Strautmann
