# Project Documentation Map

Quick reference guide for all project documentation - "What to read when"

## Start Here

| Goal | Read This | Time |
|------|-----------|------|
| **Quick overview** | [README.md](./README.md) | 5 min |
| **Get it running** | [QUICK_START.md](./QUICK_START.md) | 10 min |
| **Understand the system** | [CLAUDE.md](./CLAUDE.md) | 20 min |
| **Check current status** | [.hive-mind/FINAL_STATUS_REPORT.md](./.hive-mind/FINAL_STATUS_REPORT.md) | 10 min |

---

## By Purpose

### I want to understand what this project is

**Primary**: [CLAUDE.md](./CLAUDE.md)
- Complete project specification
- Architecture diagrams
- Core principles
- Design decisions
- All phases completed

**Secondary**: [README.md](./README.md)
- Quick project overview
- Key features
- Quick start instructions

---

### I want to set it up and run it

**Start here**: [QUICK_START.md](./QUICK_START.md)
- Environment setup
- Installation steps
- Starting the MCP server
- Configuration
- Testing

**Detailed Info**: [semantic-layer/README.md](./semantic-layer/README.md)
- Semantic layer specific setup
- Running tests
- Running examples

---

### I want to understand the current status

**Authoritative Source**: [.hive-mind/FINAL_STATUS_REPORT.md](./.hive-mind/FINAL_STATUS_REPORT.md)
- Project completion status (100%)
- Test results (7/7 passing)
- Component status
- Performance metrics
- Production readiness

**Additional Status**: [.hive-mind/SESSION_SUMMARY.md](./.hive-mind/SESSION_SUMMARY.md)
- Latest session information
- Work completed in final session

---

### I want to learn about the semantic layer

**Overview**: [semantic-layer/README.md](./semantic-layer/README.md)
- Semantic layer overview
- Model structure
- Query patterns

**Design Guide**: [semantic-layer/SEMANTIC_MODEL_DOCUMENTATION.md](./semantic-layer/SEMANTIC_MODEL_DOCUMENTATION.md)
- Semantic model design
- Following Rasmus principles
- Dimension and measure definitions

**Design Decisions**: [semantic-layer/SEMANTIC_MODEL_DECISIONS.md](./semantic-layer/SEMANTIC_MODEL_DECISIONS.md)
- Why specific decisions were made
- Tradeoffs considered
- Integration patterns

**Navigation**: [semantic-layer/DOCUMENTATION_MAP.md](./semantic-layer/DOCUMENTATION_MAP.md)
- Semantic-layer specific documentation guide

---

### I want to understand the semantic layer research

**Complete Research**: [SEMANTIC_LAYER_RESEARCH.md](./SEMANTIC_LAYER_RESEARCH.md)
- Rasmus's semantic layer principles
- Boring Semantic Layer analysis
- Ibis integration
- Design patterns
- Mercury learnings applied

---

### I want to see how the system was built

**Process Overview**: [DATA_SCIENCE_NOTEBOOK_STYLE_GUIDE.md](./DATA_SCIENCE_NOTEBOOK_STYLE_GUIDE.md)
- Data science notebook patterns
- Natural language communication
- Build → Execute → Annotate workflow
- Incremental exploration

**Agent Work**: [.hive-mind/agents/](./.hive-mind/agents/)
- Individual agent progress reports
- Work breakdown by agent
- Task completion details

**Agent Index**: [.hive-mind/INDEX.md](./.hive-mind/INDEX.md)
- Navigation for all .hive-mind documents
- Agent progress links
- Technical specs location

---

### I want technical specifications

**All Specs Location**: [.hive-mind/specs/](./.hive-mind/specs/)

| Component | Spec |
|-----------|------|
| Conversation Memory | [conversation_memory_spec.md](./.hive-mind/specs/conversation_memory_spec.md) |
| Intelligence Engine | [intelligence_engine_spec.md](./.hive-mind/specs/intelligence_engine_spec.md) |
| Semantic Layer | [semantic_layer_spec.md](./.hive-mind/specs/semantic_layer_spec.md) |
| Statistical Tester | [statistical_tester_spec.md](./.hive-mind/specs/statistical_tester_spec.md) |
| Workflow Orchestrator | [workflow_orchestrator_spec.md](./.hive-mind/specs/workflow_orchestrator_spec.md) |

---

### I want to understand system knowledge and memory

**Complete System Memory**: [.hive-mind/COLLECTIVE_MEMORY.md](./.hive-mind/COLLECTIVE_MEMORY.md)
- Comprehensive system knowledge
- Component relationships
- Integration patterns
- Performance characteristics

**Configuration**: [.hive-mind/SWARM_CONFIG.md](./.hive-mind/SWARM_CONFIG.md)
- Hive-mind swarm setup
- Agent configuration
- System parameters

---

### I want to see research on related platforms

**WrenAI Analysis**: [.hive-mind/research/](./.hive-mind/research/)
- WrenAI platform deep dive
- Reusable components analysis
- Integration opportunities

**Index**: [.hive-mind/INDEX.md](./.hive-mind/INDEX.md) - Research section

---

### I want to understand what was archived and why

**Root Archive**: [archive/outdated-summaries/README.md](./archive/outdated-summaries/README.md)
- Lists all archived documents
- Explains why they were archived
- Points to current authoritative sources

**Semantic Layer Archive**: [semantic-layer/archive/old-docs/README.md](./semantic-layer/archive/old-docs/README.md)
- Phase completion documents (now outdated)
- Internal documentation process docs
- Test plans and results (superseded by current tests)

---

## Directory Structure Overview

```
claude-analyst/
├── README.md                          # Project overview
├── QUICK_START.md                     # Setup and run instructions
├── CLAUDE.md                          # Complete specification and architecture
├── DOCUMENTATION_MAP.md               # This file
├── DATA_SCIENCE_NOTEBOOK_STYLE_GUIDE.md
├── SEMANTIC_LAYER_RESEARCH.md         # Complete research docs
│
├── .hive-mind/                        # Agent swarm working memory
│   ├── INDEX.md                       # Navigation for all .hive-mind docs
│   ├── FINAL_STATUS_REPORT.md         # ⭐ Authoritative final status
│   ├── SESSION_SUMMARY.md
│   ├── COLLECTIVE_MEMORY.md
│   ├── SWARM_CONFIG.md
│   ├── agents/                        # Individual agent progress
│   ├── specs/                         # Technical specifications
│   ├── research/                      # Technical research
│   └── memory/                        # Agent memory databases
│
├── semantic-layer/                    # Main implementation
│   ├── README.md
│   ├── DOCUMENTATION_MAP.md           # Semantic-layer specific guide
│   ├── SEMANTIC_MODEL_DOCUMENTATION.md
│   ├── SEMANTIC_MODEL_DECISIONS.md
│   ├── DESIGN_NOTES.md
│   ├── PERFORMANCE_SUMMARY.md
│   ├── models/                        # Semantic models (YAML)
│   ├── mcp_server/                    # FastMCP server
│   ├── data/                          # DuckDB database
│   ├── docs/                          # Additional docs
│   ├── tests/                         # Test fixtures
│   ├── examples/                      # Usage examples
│   ├── archive/old-docs/              # Archived semantic-layer docs
│   └── [test files].py
│
├── archive/
│   └── outdated-summaries/            # Archived root-level docs
│       └── README.md                  # Archive explanation
│
├── scripts/                           # Utility scripts
├── package.json
└── [configuration files]
```

---

## Key Navigation Paths

### For New Users
1. [README.md](./README.md) - What is this?
2. [QUICK_START.md](./QUICK_START.md) - How do I run it?
3. [CLAUDE.md](./CLAUDE.md) - How does it work?
4. [.hive-mind/FINAL_STATUS_REPORT.md](./.hive-mind/FINAL_STATUS_REPORT.md) - What's the status?

### For Developers
1. [CLAUDE.md](./CLAUDE.md) - System architecture
2. [semantic-layer/README.md](./semantic-layer/README.md) - Setup
3. [.hive-mind/INDEX.md](./.hive-mind/INDEX.md) - Technical specs
4. [semantic-layer/DOCUMENTATION_MAP.md](./semantic-layer/DOCUMENTATION_MAP.md) - Code navigation

### For Researchers/Analysts
1. [SEMANTIC_LAYER_RESEARCH.md](./SEMANTIC_LAYER_RESEARCH.md) - Research base
2. [.hive-mind/research/](./.hive-mind/research/) - Detailed research
3. [CLAUDE.md](./CLAUDE.md) - How it applies to this project

### For Understanding History
1. [.hive-mind/FINAL_STATUS_REPORT.md](./.hive-mind/FINAL_STATUS_REPORT.md) - Current status
2. [.hive-mind/agents/](./.hive-mind/agents/) - Agent work progress
3. [archive/outdated-summaries/README.md](./archive/outdated-summaries/README.md) - Archived docs

---

## Document Reference

### Core Project Documentation
- **CLAUDE.md** - Complete project specification (this is the authoritative source)
- **README.md** - Project overview and features
- **QUICK_START.md** - Setup and running instructions

### Research & Design
- **SEMANTIC_LAYER_RESEARCH.md** - Complete semantic layer research
- **DATA_SCIENCE_NOTEBOOK_STYLE_GUIDE.md** - Communication patterns
- **semantic-layer/SEMANTIC_MODEL_DOCUMENTATION.md** - Model design
- **semantic-layer/SEMANTIC_MODEL_DECISIONS.md** - Design decisions

### Current Status
- **.hive-mind/FINAL_STATUS_REPORT.md** - Authoritative final status ✅
- **.hive-mind/SESSION_SUMMARY.md** - Latest session info
- **.hive-mind/COLLECTIVE_MEMORY.md** - System knowledge base

### Technical Deep Dives
- **.hive-mind/specs/** - Component specifications
- **.hive-mind/agents/** - Detailed agent work
- **semantic-layer/DOCUMENTATION_MAP.md** - Code-level documentation

### Archived (Historical Reference)
- **archive/outdated-summaries/** - Root-level archived docs
- **semantic-layer/archive/old-docs/** - Phase completion docs

---

## Getting Help

- **"I don't know where to start"** → [README.md](./README.md)
- **"I want to run it"** → [QUICK_START.md](./QUICK_START.md)
- **"What's the status?"** → [.hive-mind/FINAL_STATUS_REPORT.md](./.hive-mind/FINAL_STATUS_REPORT.md)
- **"How does it work?"** → [CLAUDE.md](./CLAUDE.md)
- **"What's the architecture?"** → [CLAUDE.md](./CLAUDE.md) (System Architecture section)
- **"How do I find specific docs?"** → [.hive-mind/INDEX.md](./.hive-mind/INDEX.md)

---

**Last Updated**: November 12, 2025
**Project Status**: ✅ Production Ready | 100% Complete | All Tests Passing
**Authoritative Status**: [.hive-mind/FINAL_STATUS_REPORT.md](./.hive-mind/FINAL_STATUS_REPORT.md)
