# Collective Memory - AI Analyst Hive-Mind

**Mission**: Design and implement a fully native Claude Desktop AI Analyst that learns from interactions and is grounded by a semantic layer

**Established**: 2025-11-11
**Status**: Active | Phase 5 Planning

---

## Core Principles

### 1. Execution-First (Mercury Pattern)
- Build → Execute → Annotate
- Never fabricate observations
- All insights from real data

### 2. Statistical Rigor by Default
- Auto-significance testing
- Effect sizes and confidence intervals
- Sample size validation

### 3. Incremental Exploration
- One question per turn
- Each result informs next question
- Show the exploration process

### 4. Natural Language Communication
- Concise observations ("Tech 2x higher" not "Technology demonstrates...")
- Show queries and results
- Progressive disclosure

---

## System Architecture

### Current State (v1.0 - COMPLETE)
```
Claude Desktop → MCP (23 Tools) → FastMCP Server → Semantic Layer → DuckDB
  ├─ Multi-Query Workflow Orchestration (3 workflows)
  ├─ Query Optimization Engine (95% cache hit rate)
  ├─ Conversation Memory (24-hour context)
  ├─ Intelligence Layer (statistical testing, NLG)
  └─ Semantic Layer (product analytics models)
```

### Target State (v2.0 - IN PLANNING)
```
Claude Desktop → Enhanced MCP Server → Multi-Database Layer
  ├─ Stateful Query Processor (8 states) 🆕
  ├─ Hybrid Query Engine (Semantic + SQL) 🆕
  ├─ RAG Model Discovery (vector search) 🆕
  ├─ Visualization Layer (Text-to-Chart) 🆕
  ├─ Runtime Metric Definitions 🆕
  ├─ AgentDB Memory Integration 🆕
  ├─ Multi-Database Connectors (Postgres, BigQuery, etc.) 🆕
  └─ All v1.0 capabilities (preserved)
```

---

## Research Findings

### WrenAI Analysis (Complete)
**Document**: `.hive-mind/research/WRENAI_ANALYSIS.md`

**Key Learnings**:
1. State machine architecture for explicit query progression
2. SQL validation with dry-run + correction loops
3. MDL (Modeling Definition Language) for semantic governance
4. RAG with schema embeddings for model discovery
5. Multi-database support (10+ types)

**Strategic Decision**: Adopt WrenAI patterns selectively while preserving Claude-Analyst differentiators

**Competitive Advantages to Preserve**:
- ✅ Statistical rigor (auto-testing)
- ✅ Query optimization (95% cache hit rate)
- ✅ Conversation memory (24-hour context)
- ✅ Multi-query workflows
- ✅ Execution-first pattern

**Capabilities to Add**:
- 🆕 State machine architecture
- 🆕 SQL validation layer
- 🆕 RAG model discovery
- 🆕 Runtime metric definitions
- 🆕 Visualization layer
- 🆕 Multi-database connectors

---

## Agent Roles & Coordination

### Agent Types

1. **Architect Agent**
   - Design system components
   - Create technical specifications
   - Ensure architectural coherence

2. **Implementation Agent**
   - Write production code
   - Follow TDD practices
   - Implement features from specs

3. **Integration Agent**
   - AgentDB memory system integration
   - MCP tool enhancements
   - Cross-component coordination

4. **Testing Agent**
   - Comprehensive test coverage
   - Performance benchmarking
   - Validation of statistical correctness

5. **Documentation Agent**
   - User guides and API docs
   - Architecture diagrams
   - Example workflows

### Coordination Protocol

**Communication**: Via shared memory files in `.hive-mind/memory/`

**Synchronization**: Each agent reads collective memory before acting

**Conflict Resolution**: Architect agent has final say on design decisions

**Progress Tracking**: All agents update `.hive-mind/SESSION_SUMMARY.md`

---

## Implementation Phases

### Phase 5.1: State Machine & Validation (Weeks 1-2)
**Status**: Planning
**Owner**: Architect + Implementation Agents
**Deliverables**:
- StatefulQueryProcessor implementation
- QueryValidator with dry-run capability
- Enhanced error handling with state context

### Phase 5.2: RAG Model Discovery (Week 3)
**Status**: Not Started
**Owner**: Implementation + Integration Agents
**Deliverables**:
- Model embedding system
- Vector search for model discovery
- Auto-model selection in queries

### Phase 5.3: Runtime Metric Definitions (Week 4)
**Status**: Not Started
**Owner**: Implementation Agent
**Deliverables**:
- Runtime metric registry
- MCP tools for metric management
- Persistence layer

### Phase 5.4: Hybrid SQL + Ibis Mode (Weeks 5-6)
**Status**: Not Started
**Owner**: Architect + Implementation Agents
**Deliverables**:
- HybridQueryEngine
- SQL generation with LLM fallback
- Validation integration

### Phase 5.5: Visualization Layer (Week 7)
**Status**: Not Started
**Owner**: Implementation Agent
**Deliverables**:
- Chart type inference
- Plotly/Matplotlib generation
- MCP visualization tools

### Phase 5.6: Multi-Database Support (Weeks 8-9)
**Status**: Not Started
**Owner**: Integration Agent
**Deliverables**:
- DatabaseConnector interface
- Postgres, BigQuery, Snowflake connectors
- Cross-database query support

### Phase 5.7: AgentDB Integration (Week 10)
**Status**: Planning
**Owner**: Integration Agent
**Deliverables**:
- AgentDB memory layer
- Pattern storage and retrieval
- Learning from analytical workflows

---

## Technical Patterns

### State Machine Pattern
```python
class QueryState(Enum):
    UNDERSTANDING = "understanding"
    PLANNING = "planning"
    RETRIEVING = "retrieving"
    BUILDING = "building"
    OPTIMIZING = "optimizing"
    EXECUTING = "executing"
    ANALYZING = "analyzing"
    SYNTHESIZING = "synthesizing"
    FINISHED = "finished"
```

### Validation Pattern
```python
class QueryValidator:
    async def validate(self, query):
        # 1. Dry-run (EXPLAIN without fetching)
        # 2. Check complexity
        # 3. Validate schema
        # 4. Estimate result size
        return ValidationResult(ok=True/False, errors=[...])
```

### Hybrid Execution Pattern
```python
class HybridQueryEngine:
    async def execute(self, question):
        try:
            # Try semantic model (safe, fast)
            return await self.semantic_execution(question)
        except SemanticModelError:
            # Fall back to SQL generation (flexible)
            sql = await self.generate_sql(question)
            await self.validate_sql(sql)
            return await self.execute_sql(sql)
```

### RAG Pattern
```python
# Embed models once
model_embeddings = embed_semantic_models()

# Search at query time
relevant_models = vector_search(
    query=embed(user_question),
    corpus=model_embeddings,
    k=3
)
```

---

## Success Metrics

### Performance
- Query response time: <100ms for cached, <3s for new queries
- Cache hit rate: Maintain 95%+
- State transition time: <10ms per state

### Accuracy
- Model discovery: >95% correct model selection
- SQL validation: Catch 90%+ of errors before execution
- Statistical tests: 100% correct significance calculations

### Usability
- Error messages: Include helpful state context
- Progress tracking: Real-time updates in Claude Desktop
- Visualization: Auto-detect correct chart type 90%+ of the time

### Scalability
- Support 50+ semantic models without performance degradation
- Handle 5+ concurrent database connections
- Process 1000+ queries/day per user

---

## Risk Register

### Technical Risks

1. **SQL Generation Hallucinations** (Severity: High)
   - Mitigation: Validation layer with dry-run testing
   - Fallback: Reject invalid SQL, ask user for clarification

2. **Performance Degradation** (Severity: Medium)
   - Mitigation: Comprehensive benchmarking before release
   - Monitoring: Track query times, cache hit rates

3. **Multi-Database Credential Management** (Severity: High)
   - Mitigation: Secure credential storage (keyring, encrypted)
   - Validation: Security review before Phase 5.6 release

### Process Risks

1. **Feature Creep** (Severity: Medium)
   - Mitigation: Strict adherence to phase deliverables
   - Decision: Architect agent approves all scope changes

2. **Agent Coordination Failures** (Severity: Low)
   - Mitigation: Clear communication protocol via shared memory
   - Monitoring: Daily sync via SESSION_SUMMARY.md

---

## Knowledge Base

### External References
- **WrenAI**: https://github.com/Canner/WrenAI
- **Rasmus Semantic Layers**: https://rasmusengelbrecht.substack.com/
- **AgentDB**: https://agentdb.ruv.io/
- **Claude-Flow**: npx claude-flow@alpha
- **Agentic-Flow**: npx agentic-flow

### Internal Documents
- `CLAUDE.md` - Project overview and status
- `SEMANTIC_LAYER_RESEARCH.md` - Semantic layer patterns
- `DATA_SCIENCE_NOTEBOOK_STYLE_GUIDE.md` - Communication style
- `.hive-mind/research/WRENAI_ANALYSIS.md` - WrenAI analysis

### Mercury Learnings
- Build → Execute → Annotate (execution-first)
- Incremental exploration (one question per turn)
- Statistical rigor (auto-test comparisons)
- Natural language (concise, authentic)

---

## Decisions Log

### 2025-11-11: WrenAI Pattern Adoption
**Decision**: Adopt state machine, SQL validation, RAG discovery, runtime metrics
**Rationale**: These enhance Claude-Analyst without compromising differentiators
**Approved By**: Architect Agent (consensus)

### 2025-11-11: Preserve Statistical Rigor
**Decision**: Keep all statistical testing capabilities from v1.0
**Rationale**: This is our key competitive advantage over WrenAI
**Approved By**: All Agents (unanimous)

### 2025-11-11: Hybrid SQL + Ibis Approach
**Decision**: Implement dual-mode query execution (semantic preferred, SQL fallback)
**Rationale**: Best of both worlds - safety + flexibility
**Approved By**: Architect Agent

### 2025-11-11: AgentDB Integration
**Decision**: Integrate AgentDB for persistent memory and pattern learning
**Rationale**: Enables cross-session learning and analytical pattern recognition
**Approved By**: Integration Agent (proposed), Architect Agent (approved)

---

## Active Session

**Session ID**: 2025-11-11-hivemind-init
**Agents Active**: 5 (Architect, Implementation, Integration, Testing, Documentation)
**Current Focus**: Phase 5.1 Planning (State Machine & Validation)
**Next Milestone**: Complete Phase 5.1 specification by 2025-11-15

---

*This collective memory is maintained by all agents and serves as the single source of truth for the hive-mind.*
