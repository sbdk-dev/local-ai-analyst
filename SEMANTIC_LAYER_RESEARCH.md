# Semantic Layer Architecture & MCP Integration Research

**Research Date**: 2025-11-05
**Focus**: Building AI analyst systems with semantic layer integration via Model Context Protocol (MCP)

---

## Executive Summary

This research covers the emerging ecosystem of semantic layers, data abstraction frameworks, and their integration with AI assistants through the Model Context Protocol. Key findings:

1. **Semantic layers solve metric consistency problems** by providing a single source of truth for business definitions
2. **Boring Semantic Layer + Ibis** offers a lightweight, Python-native, backend-agnostic solution
3. **MCP enables reliable AI data access** by constraining LLMs to governed query patterns
4. **FastMCP provides production-ready tooling** for building enterprise MCP servers
5. **Evidence.dev represents BI-as-code** evolution with potential MCP integration opportunities

---

## Table of Contents

1. [Semantic Layer Fundamentals](#semantic-layer-fundamentals)
2. [Boring Semantic Layer](#boring-semantic-layer)
3. [Ibis Interface Layer](#ibis-interface-layer)
4. [Model Context Protocol (MCP)](#model-context-protocol-mcp)
5. [FastMCP Framework](#fastmcp-framework)
6. [Evidence.dev](#evidencedev)
7. [Deepnote Integration](#deepnote-integration)
8. [Architecture Patterns](#architecture-patterns)
9. [Implementation Roadmap](#implementation-roadmap)
10. [References](#references)

---

## Semantic Layer Fundamentals

### What Problems Do Semantic Layers Solve?

**Core Problem**: Metric inconsistency across teams. When marketing, finance, and product each calculate "churn" differently, organizations lack a single source of truth. This fragmentation wastes resources resolving definitional disputes rather than analyzing data.

**Solution**: A semantic layer acts as a "translation layer between raw data (tables, columns, SQL) and the language of your business," converting business questions into database queries automatically.

### Key Benefits

- **Eliminates metric fragmentation**: Define once, use everywhere
- **Reduces SQL complexity**: Users request metrics by name, not write SELECT statements
- **Enables rapid development**: Dashboards/reports leverage pre-defined metrics
- **Facilitates AI integration**: LLMs can query using business terms, not SQL
- **Centralizes governance**: Access controls and business logic in one place

### Core Architectural Components

```
┌─────────────────────────────────────────────────┐
│         Access Interface Layer                   │
│  (SQL, Python API, Dashboards, AI Assistants)   │
└─────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│         Query Translation Engine                 │
│  (Converts business requests → optimized SQL)   │
└─────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│         Metrics Definition Layer                 │
│  (Centralized metric specifications)            │
└─────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│         Dimensional Model Layer                  │
│  (Dimensions, relationships, aggregations)      │
└─────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│         Target Database                          │
│  (DuckDB, BigQuery, Snowflake, Postgres, etc.)  │
└─────────────────────────────────────────────────┘
```

### Design Principles

1. **Centralization**: All logic lives centrally; anyone querying uses the same definitions
2. **Abstraction**: Hide SQL complexity; expose business concepts
3. **Flexibility**: Same semantic layer runs against multiple database engines
4. **Transparency**: Generated SQL remains visible for auditing and optimization

### Semantic Layer Landscape

**Open Source Options**:
- **Boring Semantic Layer** (lightweight, Python, Ibis-based)
- **Cube.dev** (comprehensive platform, requires service hosting)
- **dbt Semantic Layer** (MetricFlow integration)
- **Malloy** (Google project, unique syntax)
- **DataJunction** (graph-based approach)

**Proprietary/Cloud**:
- **Snowflake Semantic Layer** (Snowflake ecosystem)
- **Databricks Unity Catalog** (Databricks platform)
- **Looker LookML** (Google Cloud)
- **AtScale** (enterprise semantic layer)

**Emerging Standards**:
- **Open Semantic Interchange (OSI)**: Snowflake-led initiative for vendor-neutral semantic layer standards
- Potential to commoditize proprietary solutions and enable tool interoperability

### Best Practices

#### Data Modeling
- Use dimensional modeling (facts and dimensions)
- Ingest from multiple sources
- Transform and prep data for accuracy
- Structure data to simplify complex relationships

#### Metrics Definition
- Establish single authoritative definitions
- Prevent "metrics sprawl" (multiple conflicting definitions)
- Iterate frequently but maintain governance
- Include comprehensive descriptions for AI consumption

#### Dimensions
- Maintain consistency across all metrics
- Define entities as the "nouns" of your project
- Create clear hierarchies (e.g., Country → Region → City)
- Document relationships between dimensions

#### Governance
- Engage stakeholders from all departments
- Establish robust framework (policies, procedures, standards)
- Centralize data definitions and access controls
- Enforce governance policies through semantic layer

---

## Boring Semantic Layer

### Overview

**Creator**: Julien Hurault (freelance data engineer, Geneva)
**Philosophy**: Lightweight, simple, composable semantic layer built on Ibis
**License**: Open source
**Repository**: https://github.com/boringdata/boring-semantic-layer
**Collaboration**: xorq-labs + boringdata

### What Problems It Solves

**Primary Issue**: LLMs struggle to generate correct SQL queries when retrieving data from databases. Common problems:
- Misinterpreting join relationships
- Confusion about column meanings/context
- Inconsistent aggregation logic
- Hallucinated table/column names

**Solution**: Enforce consistent data access patterns through a semantic layer, reducing LLM error rates while maintaining query reliability.

### Core Design Philosophy

Two main differentiators:
1. **Lightweight**: "Just `pip install boring-semantic-layer`"
2. **Backend-agnostic**: Built on Ibis, supporting multiple database engines without modification

The creators "wanted a simple Python package that I can use directly within my MCP implementation."

### Architecture

```python
# Semantic Model Definition
from boring_semantic_layer import to_semantic_table

flights = (
    to_semantic_table(flights_tbl, name="flights")
    .with_dimensions(
        origin=lambda t: t.origin,
        destination=lambda t: t.destination,
        carrier=lambda t: t.carrier
    )
    .with_measures(
        flight_count=lambda t: t.count(),
        total_revenue=lambda t: t.revenue.sum()
    )
)

# Query Execution
result_df = (
    flights
    .group_by("origin")
    .aggregate("flight_count")
    .execute()
)
```

**Key Components**:
- **Dimensions**: Describe data slicing ("flights by origin")
- **Measures**: Define aggregations and calculations ("total_revenue")
- **Ibis expressions**: Python functions representing database operations
- **Query method**: Combines dimensions and measures to retrieve data

### Integration with Ibis

Each semantic model is constructed on top of an Ibis table, enabling support for any backend Ibis integrates with:
- DuckDB
- BigQuery
- Snowflake
- PostgreSQL
- MySQL
- Databricks
- And 15+ more

Dimensions and measures are "expressed as Ibis expressions — which are Python functions representing database operations," providing clean, database-agnostic logic representation.

### API Patterns

**Basic Query**:
```python
flights.query(
    dimensions=["origin", "destination"],
    measures=["flight_count"]
)
```

**Filtering Options**:

1. **Ibis Expressions** (programmatic):
```python
flights.query(
    dimensions=["origin"],
    measures=["flight_count"],
    filters=[flights.origin == "JFK"]
)
```

2. **JSON-based Filtering** (LLM-friendly):
```python
flights.query(
    dimensions=["origin"],
    measures=["flight_count"],
    filters={"origin": {"eq": "JFK"}}
)
```

3. **Time-based Queries**:
```python
flights.query(
    time_dimensions=["flight_date"],
    time_range=("2024-01-01", "2024-12-31"),
    time_grain="month",
    measures=["flight_count"]
)
```

### MCP Integration

The Boring Semantic Layer includes native MCP support through the `MCPSemanticModel` class.

#### Architecture Flow

```
User Question → Claude
       ↓
Claude scans MCP tools → Selects appropriate tool
       ↓
MCP forwards query → Boring Semantic Layer
       ↓
BSL translates to SQL → DuckDB/BigQuery/etc.
       ↓
Results → MCP → Claude → Natural language response
```

#### MCPSemanticModel Class

Inherits from Anthropic's `FastMCP` class and extends it with pre-built tools:

```python
from boring_semantic_layer.mcp import MCPSemanticModel

mcp = MCPSemanticModel(semantic_model=flights)
```

#### Built-in MCP Tools

1. **list_models**: Returns available semantic models
2. **get_model**: Retrieves specific semantic model definitions
3. **get_time_range**: Provides data coverage timeframes for models
4. **query_model**: Executes queries against semantic models
   - Proper docstring prompts explaining JSON formatting
   - Filter syntax documentation
   - Available time ranges

#### Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "flights_semantic_layer": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/project",
        "run",
        "python",
        "-m",
        "boring_semantic_layer.mcp_server"
      ]
    }
  }
}
```

#### Example Usage

User asks Claude: "What are the top 10 flight destinations?"

Claude automatically:
1. Calls `get_model` to understand available dimensions/measures
2. Constructs `query_model` call with appropriate parameters
3. Receives results and formats response in natural language

### Benefits and Tradeoffs

**Benefits**:
- Trades SQL flexibility for reliability
- Prevents hallucinations (incorrect joins, bad aggregations)
- Pre-validated aggregations and relationships
- Consistent metric definitions across all queries
- Backend-agnostic (works with any Ibis-supported database)

**Tradeoffs**:
- Semantic models become the bottleneck for analytics
- Limited to pre-defined dimensions and measures
- Requires upfront model definition effort
- May not support all SQL edge cases

### Future Roadmap

Planned additions:
- YAML interface for model definitions
- Charting support (Altair, Plotly)
- Materialization and caching capabilities
- Incremental semantic layer building based on user questions

### Installation

```bash
pip install boring-semantic-layer
# or with examples
pip install 'boring-semantic-layer[examples]'
```

### Comparison to Alternatives

| Feature | Boring SL | dbt MetricFlow | Cube.dev | Malloy |
|---------|-----------|----------------|----------|---------|
| Open Source | ✅ | ✅ | ✅ | ✅ |
| Lightweight | ✅ | ❌ | ❌ | ✅ |
| Python-native | ✅ | ❌ | ❌ | ❌ |
| Backend-agnostic | ✅ | Partial | Partial | Partial |
| MCP Support | ✅ | ✅ | ✅ | ❌ |
| Requires Service | ❌ | ❌ | ✅ | ❌ |
| LLM-friendly | ✅ | Partial | ✅ | ❌ |

---

## Ibis Interface Layer

### Overview

**Project**: Ibis Project (https://ibis-project.org)
**Description**: "The portable Python dataframe library"
**Purpose**: Write dataframe code once, execute across 20+ backends
**License**: Open source

### What Problems Does Ibis Solve?

**Core Problem**: Vendor lock-in and platform fragmentation in data work. Teams must learn different APIs for:
- pandas (local development)
- PySpark (Databricks/EMR)
- BigQuery SQL (Google Cloud)
- Snowflake SQL (Snowflake)
- Polars (high-performance local)

**Solution**: Unified Python dataframe API that compiles to backend-native SQL/operations. "Iterate locally and deploy remotely by changing a single line of code."

### Core Architecture

**Decoupled Design Principle**: Separate dataframe API from backend execution.

```
┌─────────────────────────────────────┐
│    Unified Python Dataframe API      │
│  (Similar to pandas, consistent)     │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│   Expression Compilation Layer       │
│  (Lazy evaluation, optimization)     │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│   SQLGlot SQL Generation             │
│  (Dialect-specific SQL compilation)  │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│   Backend Execution                  │
│  (DuckDB, BigQuery, Snowflake, etc.) │
└─────────────────────────────────────┘
```

### API Patterns

**Basic Workflow**:
```python
import ibis

# Read data (defaults to DuckDB)
t = ibis.read_parquet("penguins.parquet")

# Dataframe operations (lazy evaluation)
result = (
    t
    .filter(t.species == "Adelie")
    .group_by("island")
    .agg(count=t.count(), avg_mass=t.body_mass_g.mean())
)

# Execute and retrieve results
df = result.execute()
```

**Method Chaining**:
```python
(
    t
    .filter(t.year >= 2008)
    .select(["species", "island", "bill_length_mm"])
    .group_by(["species", "island"])
    .agg(avg_bill=ibis._.bill_length_mm.mean())
    .order_by(ibis.desc("avg_bill"))
    .head(10)
)
```

**Mixing SQL and Python**:
```python
# Embed raw SQL strings
sql_expr = ibis.sql("SELECT * FROM penguins WHERE species = 'Adelie'")

# Continue with Python operations
result = sql_expr.group_by("island").count()
```

### Backend Support

**Three Categories**:

1. **OLTP Databases**:
   - PostgreSQL
   - MySQL
   - Microsoft SQL Server
   - Oracle
   - SQLite

2. **Data Warehouses**:
   - BigQuery
   - Snowflake
   - Redshift (via Trino)
   - Databricks

3. **DataFrame/Analytics Engines**:
   - DuckDB (default)
   - Polars
   - PySpark
   - Dask
   - DataFusion
   - Apache Flink

4. **Specialized Systems**:
   - ClickHouse
   - Apache Druid
   - Trino/Presto
   - Exasol
   - RisingWave
   - Apache Impala

**Operation Support Matrix**: Feature support varies by backend. Ibis handles graceful degradation or allows backend switching based on requirements.

### Design Patterns

**Lazy Evaluation**:
- Expressions build query plans without executing
- Optimization occurs before sending to backend
- `.execute()` triggers actual computation

**Interactive Mode**:
- Exploratory data analysis in notebooks
- Automatic result display
- SQL inspection capabilities

**Schema Inspection**:
```python
# View generated SQL
print(result.compile())

# Inspect schema
result.schema()
```

### Relationship to Semantic Layers

Ibis functions as a **semantic abstraction layer** by:

1. **Normalizing operations**: Translating Python expressions into backend-native SQL
2. **Abstracting dialect differences**: Handling PostgreSQL-specific syntax differently than T-SQL
3. **Providing logical-to-physical mapping**: Users think in dataframe operations; Ibis handles execution details

This positions Ibis as the **foundation for semantic layers** like Boring Semantic Layer, which adds business logic on top of Ibis's technical abstraction.

### Integration Patterns

**Visualization**:
- Altair
- Plotly
- matplotlib
- seaborn
- plotnine
- Streamlit

**SQL Integration**:
```python
# Embed SQL strings as first-class citizens
ibis.sql("""
    SELECT species, COUNT(*) as cnt
    FROM penguins
    GROUP BY species
""").join(other_table, "species")
```

**Multi-backend Workflows**:
```python
# Development: DuckDB
dev_conn = ibis.duckdb.connect()
dev_table = dev_conn.read_parquet("local_data.parquet")

# Production: BigQuery (same code)
prod_conn = ibis.bigquery.connect(project="my-project")
prod_table = prod_conn.table("my_dataset.my_table")

# Identical business logic
def analyze(table):
    return table.group_by("category").agg(total=table.amount.sum())

dev_result = analyze(dev_table)
prod_result = analyze(prod_table)
```

**Data Format Support**:
- Parquet
- CSV
- Cloud storage (GCS with DuckDB)
- Backend-native formats

### Key Benefits

1. **Portability**: Write once, deploy anywhere across backends
2. **Development velocity**: Same API for 20+ backends reduces context switching
3. **Performance**: Leverages each backend's native execution engine rather than Python evaluation
4. **SQL-Python bridging**: "SQL works for the heavy lifting" while "Python excels at dynamic transformations"
5. **Cost optimization**: Local DuckDB development avoids cloud costs during iteration

### Use Cases

- Data engineering pipelines requiring multi-platform deployment
- Analytics teams needing flexible backend switching
- Organizations migrating between data platforms
- Hybrid workflows combining SQL and Python paradigms
- Semantic layer foundations (Boring Semantic Layer, etc.)

### User Testimonials

> "I can run PySpark in Databricks and Polars on my laptop with identical code"
> — Ibis user testimonial

---

## Model Context Protocol (MCP)

### Overview

**Creator**: Anthropic
**Announced**: November 2024
**Type**: Open standard, open-source framework
**Purpose**: Standardize how AI systems integrate with external tools, systems, and data sources
**Website**: https://modelcontextprotocol.io

### Why MCP Was Created

**Problem**: "Even the most sophisticated models are constrained by their isolation from data—trapped behind information silos and legacy systems."

Every new data source required custom integration work. Organizations built one-off connectors for each combination of:
- AI application × Data source
- Creating N × M integration complexity

**Solution**: MCP provides a universal standard, replacing fragmented custom integrations with a single protocol.

### Core Protocol Design

**Architecture**: Open standard enabling developers to establish secure, bidirectional connections between data sources and AI-powered applications.

```
┌─────────────────────────────────────┐
│      AI Application (MCP Client)     │
│  (Claude Desktop, IDEs, Custom Apps) │
└─────────────────────────────────────┘
            ↓  ↑
         MCP Protocol
       (Bidirectional)
            ↓  ↑
┌─────────────────────────────────────┐
│      MCP Server (Data Source)        │
│  (Databases, APIs, File Systems)     │
└─────────────────────────────────────┘
```

**Key Characteristics**:
- **Client-Server Architecture**: MCP servers expose data; MCP clients (AI apps) connect
- **Bidirectional Communication**: Two-way data flow between AI and data sources
- **Transport Agnostic**: Supports Stdio, HTTP, SSE (Server-Sent Events)
- **Standardized Protocol**: Consistent interface across all implementations

### Three Core Capabilities

#### 1. Tools

**Purpose**: Functions that LLMs can execute (like POST endpoints)

**Characteristics**:
- Execute code or produce side effects
- Defined with JSON Schema for parameters
- Return structured results
- Can be synchronous or asynchronous

**Example**:
```python
@mcp.tool()
def search_database(query: str, limit: int = 10) -> list[dict]:
    """Search the database for records matching the query"""
    return execute_search(query, limit)
```

#### 2. Resources

**Purpose**: Read-only data sources (like GET endpoints)

**Characteristics**:
- Load information into LLM context
- Support URI templates with parameters
- Can be static or dynamic
- Return text or binary data

**Example**:
```python
@mcp.resource("user://{user_id}")
def get_user(user_id: str) -> str:
    """Get user profile information"""
    return json.dumps(fetch_user(user_id))
```

#### 3. Prompts

**Purpose**: Reusable message templates for LLM interactions

**Characteristics**:
- Define interaction patterns
- Can include variables
- Guide LLM behavior
- Sharable across applications

**Example**:
```python
@mcp.prompt()
def analyze_data():
    return "Analyze the following dataset and provide insights..."
```

### Client-Server Architecture

**MCP Server**:
- Exposes tools, resources, and prompts
- Handles requests from MCP clients
- Manages data source connections
- Enforces access controls

**MCP Client**:
- AI application that connects to MCP servers
- Discovers available capabilities
- Invokes tools and reads resources
- Presents results to users/LLMs

**Symmetric Design**: Allows flexible, two-way communication between AI systems and enterprise data.

### Pre-built Integrations

**Official MCP Servers**:
- **Google Drive**: Access documents and files
- **Slack**: Read messages and channels
- **GitHub**: Repository data and operations
- **Git**: Version control operations
- **Postgres**: Database queries
- **Puppeteer**: Web scraping and automation

**Community Servers**: Growing ecosystem at https://github.com/modelcontextprotocol/servers

### Claude Desktop Integration

**Configuration File Location**:
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Basic Configuration**:
```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://localhost/mydb"
      ]
    }
  }
}
```

**Multiple Servers**:
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your_token_here"
      }
    },
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://localhost/mydb"
      ]
    }
  }
}
```

**Restart Required**: After editing configuration, restart Claude Desktop for changes to take effect.

### Use Cases

**Development Tools** (Zed, Replit, Codeium, Sourcegraph):
- AI agents retrieve context around coding tasks
- "More nuanced and functional code with fewer attempts"
- Better understanding of project structure and dependencies

**Enterprise Applications**:
- Connect Claude to internal systems and datasets locally
- Claude for Work customers can test MCP servers
- Access company-specific data sources

**Data Analytics**:
- Direct semantic layer queries
- Automated data exploration
- Multi-step analytical workflows
- Agentic analytics across enterprise systems

### Early Adopters

**Block** (Square/Cash App):
> "Open technologies like the Model Context Protocol are the bridges that connect AI to real-world applications, ensuring innovation is accessible, transparent, and rooted in collaboration."
> — CTO, Block

**Apollo GraphQL**: Demonstrated MCP integration for GraphQL APIs

### Ecosystem Growth

- **Collaborative, open-source project** with community contributions
- **Growing server repository** at https://github.com/modelcontextprotocol/servers
- **Multiple SDKs**: Python, TypeScript/JavaScript
- **Integration in major tools**: Claude Desktop, development IDEs

### Future Roadmap

**Planned Developments**:
1. Developer toolkits for deploying remote production MCP servers organization-wide
2. AI systems maintaining context as they transition between tools and datasets
3. Evolution from fragmented integrations to sustainable, scalable architecture
4. Context-aware AI seamlessly accessing information regardless of data source location

### Vision

**Goal**: Enable "context-aware AI" where systems seamlessly access relevant information regardless of data source location, maintaining consistency across all interactions.

**Impact**: Replace N × M integration complexity with N + M simplicity (each data source gets one MCP server; each AI app needs one MCP client).

---

## FastMCP Framework

### Overview

**Creator**: Jeremiah Lowin (@jlowin)
**Description**: "The fast, Pythonic way to build MCP servers and clients"
**Repository**: https://github.com/jlowin/fastmcp
**Documentation**: https://gofastmcp.com
**License**: Open source
**Status**: FastMCP 2.0 is actively maintained, production-ready framework

### Core Architecture & Design Philosophy

**Philosophy**: Minimal boilerplate, maximum productivity. Developers expose Python functions as MCP tools using simple decorators. FastMCP handles protocol complexity automatically.

**Layered Approach**:
- High-level `FastMCP` class wraps the official MCP SDK
- Adds production-grade features while maintaining protocol compatibility
- Pioneered Python MCP development (concepts incorporated into official SDK)

**Design Priorities**:
1. Clean, Pythonic code
2. Reducing complexity through high-level abstractions
3. Production readiness out of the box
4. Enterprise-grade features

### Key Features

#### 1. Server Composition & Mounting

**Modular Application Design**:

```python
# Create sub-applications
users_mcp = FastMCP("Users API")
@users_mcp.tool()
def get_user(user_id: str):
    return fetch_user(user_id)

orders_mcp = FastMCP("Orders API")
@orders_mcp.tool()
def get_order(order_id: str):
    return fetch_order(order_id)

# Compose into main application
main_mcp = FastMCP("Main API")
main_mcp.mount(users_mcp)  # Live linking
main_mcp.import_server(orders_mcp)  # Static copying
```

**Benefits**:
- Organize code by domain
- Reusable components across projects
- Team-based development (different teams own different MCP instances)

#### 2. Proxying Capabilities

**Purpose**: MCP servers acting as intermediaries for other MCP servers

```python
# Proxy remote MCP server
remote_proxy = FastMCP.as_proxy(
    "https://remote-server.com/mcp",
    name="Remote Proxy"
)

# Bridge transports (e.g., remote SSE → local Stdio)
main_mcp.mount(remote_proxy)
```

**Use Cases**:
- Convert between transport types
- Add authentication/logging layers
- Aggregate multiple remote servers
- Gateway patterns for security

#### 3. OpenAPI/FastAPI Integration

**Convert OpenAPI specs to MCP servers**:
```python
# From OpenAPI spec
api_mcp = FastMCP.from_openapi(
    "https://api.example.com/openapi.json",
    name="Example API"
)

# From existing FastAPI app
from fastapi import FastAPI
app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: str):
    return {"id": user_id, "name": "Alice"}

mcp = FastMCP.from_fastapi(app)
```

**Benefits**:
- Instant MCP ecosystem exposure for web APIs
- No code rewrite required
- Automatic tool schema generation

### Authentication Patterns

**Zero-Configuration OAuth Flows** for enterprise-grade security.

#### Supported Providers

- Google
- GitHub
- Microsoft Azure
- Auth0
- WorkOS
- Descope
- JWT/Custom
- API Keys

#### Server Protection

```python
from fastmcp.server.auth.providers.google import GoogleProvider

# Configure OAuth provider
auth = GoogleProvider(
    client_id="your_client_id",
    client_secret="your_client_secret",
    base_url="https://myserver.com"
)

# Protect MCP server
mcp = FastMCP("Protected Server", auth=auth)

@mcp.tool()
def sensitive_operation():
    """Only authenticated users can call this"""
    return perform_operation()
```

#### Client Authentication

```python
from fastmcp import Client

# Connect with OAuth
async with Client("https://protected-server.com/mcp", auth="oauth") as client:
    result = await client.call_tool("sensitive_operation")
```

#### Authentication Architecture

**Full OIDC Support**:
- OpenID Connect (OIDC) compliant
- Dynamic Client Registration (DCR)
- Unique OAuth proxy pattern enabling DCR with any provider

**Security Features**:
- Token-based authentication
- Automatic token refresh
- Secure credential management
- Role-based access control (via provider)

### Deployment Strategies

#### Development

**Local Execution**:
```bash
fastmcp run server.py
```

Uses default STDIO transport for local Claude Desktop integration.

#### Production Options

**1. FastMCP Cloud**:
- Instant HTTPS endpoints
- Built-in authentication
- Zero configuration
- Free tier for personal servers
- Managed infrastructure

```python
mcp.run(transport="cloud")
```

**2. Self-Hosted HTTP**:
```python
mcp.run(transport="http", host="0.0.0.0", port=8000)
```

**3. Self-Hosted SSE**:
```python
mcp.run(transport="sse", host="0.0.0.0", port=8000)
```

**4. Custom Infrastructure**:
- Deploy to AWS Lambda, Google Cloud Functions, Azure Functions
- Run in Docker containers
- Kubernetes deployments
- Behind API gateways

### Testing Utilities

**In-Memory Testing** for efficient unit testing without process management or network calls:

```python
from fastmcp import FastMCP, Client

# Create server
mcp = FastMCP("My MCP Server")

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

# Test directly in memory
async def test_add():
    async with Client(mcp) as client:
        result = await client.call_tool("add", {"a": 5, "b": 3})
        assert result == 8
```

**Benefits**:
- Fast test execution
- No network configuration
- No process management
- Perfect for CI/CD pipelines

### Client Libraries

**FastMCP Client** provides programmatic MCP server interaction:

```python
from fastmcp import Client

# Auto-detect transport
async with Client("https://server.com/mcp") as client:
    # List available tools
    tools = await client.list_tools()

    # Call tool
    result = await client.call_tool("search", {"query": "data"})

    # List resources
    resources = await client.list_resources()

    # Read resource
    data = await client.read_resource("user://123")
```

**Supported Transports**:
- **Stdio**: Local process communication
- **SSE**: Server-Sent Events (remote servers)
- **HTTP**: Standard HTTP requests
- **In-Memory**: Direct FastMCP instance testing

**Advanced Patterns**:
- Server-initiated LLM sampling requests
- Progress reporting
- Context propagation
- Error handling

### Core Components

#### Tools

**Definition**:
```python
@mcp.tool()
def search_products(query: str, category: str = None, limit: int = 10) -> list[dict]:
    """
    Search products in the catalog.

    Args:
        query: Search query string
        category: Optional category filter
        limit: Maximum number of results (default: 10)

    Returns:
        List of matching products
    """
    return execute_search(query, category, limit)
```

**Auto-Generated Schema**: FastMCP generates JSON Schema from:
- Type hints
- Docstrings
- Default values
- Return type annotations

#### Resources

**URI Templates with Dynamic Parameters**:
```python
@mcp.resource("product://{product_id}")
def get_product(product_id: str) -> str:
    """Get detailed product information"""
    product = fetch_product(product_id)
    return json.dumps(product)

@mcp.resource("products://{category}")
def list_products(category: str) -> str:
    """List all products in a category"""
    products = fetch_products_by_category(category)
    return json.dumps(products)
```

**Usage by Claude**:
- Claude sees available resource templates
- Requests specific instances: `product://12345`
- Receives structured data in context

#### Prompts

**Reusable Message Templates**:
```python
@mcp.prompt()
def analyze_data_prompt():
    return "Analyze the following dataset and provide insights..."

@mcp.prompt()
def generate_report_prompt(report_type: str):
    return f"Generate a {report_type} report with the following sections..."
```

#### Context Object

**Injectable Context for Enhanced Capabilities**:

```python
from fastmcp import Context

@mcp.tool()
async def complex_analysis(query: str, ctx: Context):
    # Logging
    ctx.info(f"Starting analysis for: {query}")

    # Progress reporting
    ctx.report_progress(0.3, "Processing data...")

    # LLM sampling (ask Claude for help)
    suggestion = await ctx.sample("How should I interpret this data?")

    # Resource access
    data = await ctx.read_resource("data://latest")

    # Error logging
    try:
        result = perform_analysis(query, data)
    except Exception as e:
        ctx.error(f"Analysis failed: {e}")
        raise

    return result
```

**Context Capabilities**:
- **Logging**: `ctx.info()`, `ctx.error()`, `ctx.debug()`
- **LLM Sampling**: `ctx.sample()` - Ask Claude for guidance during tool execution
- **Resource Access**: `ctx.read_resource()` - Access other resources programmatically
- **Progress Reporting**: `ctx.report_progress()` - Update user on long operations

### Installation

**Recommended (via uv)**:
```bash
uv pip install fastmcp
```

**Standard pip**:
```bash
pip install fastmcp
```

**With optional dependencies**:
```bash
pip install "fastmcp[auth]"  # Authentication providers
pip install "fastmcp[cloud]"  # FastMCP Cloud deployment
```

### Minimal Example

```python
from fastmcp import FastMCP

# Create server
mcp = FastMCP("Demo 🚀")

# Add tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Add resource
@mcp.resource("greeting://{name}")
def greet(name: str) -> str:
    return f"Hello, {name}!"

# Add prompt
@mcp.prompt()
def analyze_prompt():
    return "Analyze the data and provide insights"

# Run server
if __name__ == "__main__":
    mcp.run()
```

### Comparison to Official MCP SDK

| Feature | FastMCP 2.0 | Official SDK |
|---------|-------------|--------------|
| Basic Protocol Support | ✅ | ✅ |
| Production-Grade Auth | ✅ | ❌ |
| Server Composition | ✅ | ❌ |
| Proxying | ✅ | ❌ |
| OpenAPI/FastAPI Integration | ✅ | ❌ |
| Deployment Tooling | ✅ | ❌ |
| Testing Frameworks | ✅ | Partial |
| Client Libraries | ✅ | ✅ |
| Documentation | ✅ (LLM-friendly) | ✅ |

**FastMCP 2.0 Advantages**:
- "Pioneered Python MCP development"
- "Actively maintained, production-ready framework"
- "Extends far beyond basic protocol implementation"
- Enterprise authentication and deployment features

**Official SDK Advantages**:
- Reference implementation
- Backed by Anthropic
- Minimal dependencies

### Documentation

**Primary**: https://gofastmcp.com
**LLM-Friendly Formats**:
- `llms.txt`: Concise documentation
- `llms-full.txt`: Comprehensive documentation
- Any page available as markdown by appending `.md`

---

## Evidence.dev

### Overview

**Description**: "Business Intelligence as Code"
**Website**: https://evidence.dev
**Repository**: https://github.com/evidence-dev/evidence
**License**: Open source
**Stars**: 5,300+ GitHub stars
**Downloads**: 10,000+ weekly npm downloads

### What Problems Does Evidence.dev Solve?

**Core Problem**: Gap between traditional BI tools (drag-and-drop) and modern development practices (code-based workflows).

**Traditional BI Tool Issues**:
- Version control challenges
- Limited collaboration capabilities
- Vendor lock-in
- Difficult to test and validate
- Not reproducible

**Solution**: Data teams build professional data products using code-based workflows with SQL, markdown, and modern development practices.

### Target Audience

- Analytics managers
- Data engineers
- Teams seeking to move beyond spreadsheets
- Organizations wanting version-controlled reporting
- Data teams familiar with Git workflows

### Core Features & Capabilities

#### 1. Development Experience

**Browser-Based IDE**:
- Real-time syntax validation
- Automatic error detection
- Intelligent autocomplete for components and SQL queries
- AI-enhanced development tools for schema lookup and debugging

**Code-First Approach**:
```markdown
# Sales Dashboard

```sql revenue_by_month
SELECT
    DATE_TRUNC('month', order_date) as month,
    SUM(amount) as revenue
FROM orders
GROUP BY 1
ORDER BY 1
```

Last month's revenue: **<Value data={revenue_by_month} column=revenue/>**

<LineChart
    data={revenue_by_month}
    x=month
    y=revenue
/>
```

#### 2. Output Types

**Data Products**:
- Interactive dashboards and articles
- Data applications with AI chat capabilities
- Customer/embedded analytics
- Business review documents
- Exploratory data interfaces

**Characteristics**:
- Responsive design (all device sizes)
- Clean, professional appearance
- Interactive visualizations
- AI-powered interfaces

#### 3. Performance

**Query Engine**:
- "Sub-second queries" even on millions of records
- Multi-level intelligent caching with automatic optimization
- Columnar storage with vectorized execution

**Architecture**:
- Managed lakehouse built on ClickHouse infrastructure
- Automatic scaling
- Efficient data processing

#### 4. Data Sources & Integration

**Supported Warehouses**:
- Snowflake
- BigQuery
- ClickHouse
- Redshift
- PostgreSQL
- MySQL
- DuckDB
- MotherDuck
- SQLite
- SQL Server
- Timescale
- CSV sources

**Data Refresh**:
- 15-minute intervals
- Hourly updates
- Daily syncing
- Scheduled refresh from minutes to daily

**Multiple Sources**:
- Connect to multiple data sources simultaneously
- "Universal SQL" across sources
- Build interactive data apps

#### 5. Templating & Component Model

**Declarative Markdown + Components**:

```markdown
# Component Examples

## Tables
<DataTable data={sales_data}/>

## Charts
<BarChart data={sales_data} x=category y=revenue/>
<LineChart data={timeseries} x=date y=value/>
<ScatterPlot data={correlation} x=var1 y=var2/>

## Metrics
<BigValue data={kpis} value=total_revenue/>

## Filters
<Dropdown name=region options={regions}/>
<DateRange name=dateRange/>

## AI Components
<AIChat data={dataset}/>
```

**Component Library**:
- Charts (line, bar, scatter, pie, area, etc.)
- Tables (sortable, filterable, paginated)
- Metrics (big values, KPI cards)
- Filters (dropdown, search, date range)
- Text formatting
- Images and media
- AI-powered interfaces

**Characteristics**:
- "Clean, readable SQL and markdown"
- Compiles into responsive data products
- Interactive and explorable
- Professional design by default

### Architecture

**Development Flow**:
```
SQL + Markdown Source Files
         ↓
   Evidence Compiler
         ↓
   Interactive Web App
         ↓
   Browser Rendering
```

**Query Engine Architecture**:
```
SQL Query → Evidence Parser → Query Optimization → ClickHouse Engine
                                                           ↓
                                                    Columnar Storage
                                                           ↓
                                                   Vectorized Execution
                                                           ↓
                                                    Cached Results
```

**Security**:
- Row-level security for granular data access control
- User authentication integration
- Data governance policies

### Use Cases & Examples

**Testimonials**:

> "Professional reporting for analytics teams"
> — Modern Animal

> "Client-facing data products built in days"
> — Dialogue

> "Internal business reviews and metrics presentation"
> — Apple (reported user)

**Application Types**:
- Executive dashboards
- Customer analytics portals
- Internal business reviews
- Data narratives replacing spreadsheet workflows
- Embedded analytics in products
- Automated reporting systems

### Claude Desktop & MCP Compatibility

**Current State**: The documentation doesn't explicitly discuss Claude Desktop or MCP server integration.

**Potential Compatibility**:
- ✅ Browser-based IDE with AI agents suggests API accessibility
- ✅ Open-source foundations (5.3k GitHub stars)
- ✅ Code-based workflow aligns with MCP philosophy
- ✅ Data source abstraction layer could expose MCP tools
- ⚠️ Would require external verification and potential custom integration

**Hypothetical MCP Integration**:
```python
# Potential Evidence.dev MCP Server (not official)
from fastmcp import FastMCP
from evidence_client import EvidenceClient

mcp = FastMCP("Evidence.dev Analytics")

@mcp.tool()
def query_evidence_report(report_name: str, filters: dict = None):
    """Query an Evidence.dev report with optional filters"""
    client = EvidenceClient()
    return client.query_report(report_name, filters)

@mcp.resource("report://{report_id}")
def get_report(report_id: str):
    """Get Evidence.dev report definition and data"""
    client = EvidenceClient()
    return client.get_report(report_id)
```

### Version Control & Collaboration

**Git Integration**:
- Native version control support
- Commit history tracking
- Branch-based development
- Pull request workflows

**Benefits**:
- Track changes to reports and dashboards
- Roll back to previous versions
- Collaborate across teams
- Code review processes
- CI/CD integration

### Semantic Layer Integration

**Current State**: Evidence.dev is positioned as part of the emerging generation of "modern BI tools like Sigma, Omni, Steep, and Evidence built to work with semantic layers from day one."

**Potential Integration Pattern**:
```
Evidence.dev ← → Semantic Layer (dbt, Cube, etc.) ← → Data Warehouse
```

**Benefits**:
- Consistent metric definitions across BI tools
- Single source of truth for business logic
- Reduced SQL complexity in Evidence reports
- Governance through semantic layer

### Comparison to Traditional BI

| Feature | Evidence.dev | Traditional BI |
|---------|-------------|----------------|
| Development | Code-based | Drag-and-drop |
| Version Control | Git-native | Limited/None |
| Collaboration | Developer workflows | Shared workspace |
| Testing | Automated | Manual |
| Reproducibility | ✅ | ❌ |
| Deployment | CI/CD | Manual export |
| Cost | Open source + Cloud | Enterprise licenses |

### Limitations

**Not Explicitly Mentioned but Implied**:
- Requires SQL knowledge (not for non-technical users)
- Code-based workflow has learning curve
- May not support all complex BI features
- Cloud dependency for managed version
- Limited information about self-hosting

---

## Deepnote Integration

### Overview

**Description**: "A data notebook for the AI era"
**Users**: 500,000+ professionals
**Positioning**: Jupyter successor with enhanced capabilities
**Repository**: https://github.com/deepnote/deepnote
**License**: Apache 2.0

### What is Deepnote?

**Evolution**: Jupyter notebook reimagined with:
- AI agent integration
- Improved UI/UX
- Expanded block types beyond code cells
- Native data integrations
- Real-time collaboration

**Supported Languages**:
- Python
- R
- SQL

**Environments**:
- Local IDEs (VS Code, Cursor, Windsurf)
- Cloud (Deepnote Cloud)
- JupyterLab

### Architecture Components

**Repository Structure**:

#### 1. @deepnote/blocks

**TypeScript Utilities for Notebook Block Types**:

```typescript
// Block Types
- Code (Python, R, SQL)
- Text (Markdown)
- Input (Interactive parameters)
- Visualization (Charts, graphs)
- Button (Interactive actions)
- Big Number (KPI display)
- Image (Media content)
- Separator (Visual organization)
```

**Purpose**: Modular, extensible block system replacing traditional cell-only approach.

#### 2. @deepnote/convert

**CLI and Programmatic Conversion Tools**:

```bash
# Convert .ipynb to .deepnote YAML
npx @deepnote/convert input.ipynb output.deepnote

# Convert .deepnote to .ipynb
npx @deepnote/convert input.deepnote output.ipynb
```

**Capabilities**:
- Bidirectional conversion between `.ipynb` and `.deepnote` formats
- Preserves block types and metadata
- Programmatic APIs for Node.js/TypeScript
- Python code generation from block definitions

#### 3. .deepnote Format

**YAML-based Project Format** replacing JSON:

```yaml
# example.deepnote
version: 1.0
project:
  name: "My Analysis"
  blocks:
    - type: markdown
      content: "# Sales Analysis"

    - type: code
      language: python
      content: |
        import pandas as pd
        df = pd.read_csv('sales.csv')

    - type: visualization
      chart_type: line
      data_source: df
```

**Benefits**:
- Human-readable
- Version control friendly
- Easier to review in pull requests
- Supports comments

### API & Integration Patterns

**Programmatic Conversion**:
```typescript
import { convert } from '@deepnote/convert';

// Convert in Node.js/TypeScript
const deepnoteFormat = await convert(ipynbContent, {
  from: 'ipynb',
  to: 'deepnote'
});
```

**Block-based Extensibility**:
- Open `@deepnote/blocks` package enables custom block types
- Defined schemas for each block type
- Python code generation from blocks
- Markdown conversion capabilities

**Integration Points**:
- Git integration built-in
- Export/import via CLI tools
- Programmatic APIs for automation
- Extension support for major IDEs

### Collaboration Features

**Real-time Editing**:
- Google Docs-style collaboration in Deepnote Cloud
- Multiple users editing simultaneously
- Live cursors and presence indicators
- Comment threads on blocks

**Reactive Execution**:
- Auto-reruns dependent blocks on input changes
- Dependency graph understanding
- Efficient incremental computation

**Project Organization**:
- Multiple notebooks per project
- Shared settings and environments
- Team workspaces

**Version Control**:
- Git integration
- Commit history
- Branch management
- Merge conflict resolution

### Claude Desktop/MCP Integration Potential

**Compatibility Indicators**:

✅ **Favorable**:
- Open, documented block types suitable for MCP tool definitions
- Programmatic APIs enabling external tool interaction
- Extensible design allows custom integrations
- Roadmap mentions "local AI agent" capabilities

⚠️ **Requires Investigation**:
- No explicit MCP server implementation yet
- Would require custom MCP wrapper
- API documentation needed for programmatic access

**Hypothetical MCP Integration**:

```python
from fastmcp import FastMCP
import deepnote_api  # hypothetical

mcp = FastMCP("Deepnote Integration")

@mcp.tool()
def create_deepnote_block(project_id: str, block_type: str, content: str):
    """Create a new block in a Deepnote project"""
    return deepnote_api.add_block(project_id, block_type, content)

@mcp.tool()
def execute_deepnote_code(project_id: str, block_id: str):
    """Execute a code block and return results"""
    return deepnote_api.execute_block(project_id, block_id)

@mcp.resource("project://{project_id}")
def get_project(project_id: str):
    """Get Deepnote project structure and blocks"""
    return deepnote_api.get_project(project_id).to_yaml()
```

**Potential Use Cases**:
- Claude creates/edits Deepnote blocks based on user requests
- Execute analysis code and retrieve results via MCP
- Read project structure to understand context
- Generate visualizations programmatically

### Open Source Extensibility

**Published Packages**:
- **@deepnote/blocks**: Block type definitions (npm)
- **@deepnote/convert**: Conversion utilities (npm)

**IDE Extensions**:
- vscode-deepnote (VS Code)
- jupyterlab-deepnote (JupyterLab extension)
- deepnote-toolkit (utility package)
- Support for Cursor and Windsurf

**Related Repositories**:
- Main repo: github.com/deepnote/deepnote
- VS Code extension: github.com/deepnote/vscode-deepnote
- JupyterLab extension: github.com/deepnote/jupyterlab-deepnote

**Contribution Model**:
- Apache 2.0 licensed
- Open to community contributions
- Extensible architecture encourages custom blocks
- Public APIs for integration

### Comparison to Jupyter

| Feature | Deepnote | Jupyter |
|---------|----------|---------|
| Format | YAML (.deepnote) | JSON (.ipynb) |
| Block Types | Extended (9+ types) | Code + Markdown |
| Collaboration | Real-time | None (native) |
| AI Integration | Built-in agent | Extensions only |
| Reactive Execution | ✅ | ❌ |
| Git Integration | Native | Manual |
| Version Control | YAML-friendly | JSON (merge conflicts) |
| IDE Support | Multi-IDE | Jupyter ecosystem |

### Roadmap Highlights

**Mentioned Features**:
- "Local AI agent" capabilities
- Enhanced block types
- Improved data integrations
- Performance optimizations

**Community Interest**:
- Growing ecosystem of extensions
- Active development
- Regular updates to npm packages

---

## Architecture Patterns

### 1. Semantic Layer + MCP Integration Pattern

**Overview**: The canonical pattern for building AI analyst systems that query business data reliably.

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Desktop                        │
│              (MCP Client - AI Assistant)                 │
└─────────────────────────────────────────────────────────┘
                          ↓  ↑
                     MCP Protocol
                   (Tools, Resources)
                          ↓  ↑
┌─────────────────────────────────────────────────────────┐
│                   FastMCP Server                         │
│         (Python MCP server with auth/logging)            │
└─────────────────────────────────────────────────────────┘
                          ↓  ↑
                  Python API Calls
                          ↓  ↑
┌─────────────────────────────────────────────────────────┐
│              Boring Semantic Layer                       │
│         (Business logic, metrics, dimensions)            │
└─────────────────────────────────────────────────────────┘
                          ↓  ↑
                  Ibis Expressions
                          ↓  ↑
┌─────────────────────────────────────────────────────────┐
│                    Ibis Layer                            │
│         (Database abstraction, SQL generation)           │
└─────────────────────────────────────────────────────────┘
                          ↓  ↑
                  Backend-specific SQL
                          ↓  ↑
┌─────────────────────────────────────────────────────────┐
│                   Data Warehouse                         │
│      (DuckDB, BigQuery, Snowflake, Postgres, etc.)      │
└─────────────────────────────────────────────────────────┘
```

**Key Characteristics**:

1. **Claude interacts only through governed MCP tools**
   - Cannot write arbitrary SQL
   - Limited to pre-defined dimensions and measures
   - Reduces hallucination risk

2. **Semantic layer enforces business logic**
   - Consistent metric definitions
   - Proper join relationships
   - Validated aggregation patterns

3. **Ibis provides backend flexibility**
   - Develop locally with DuckDB
   - Deploy to production with BigQuery/Snowflake
   - Same Python code, different backends

4. **FastMCP adds production features**
   - Authentication and authorization
   - Logging and monitoring
   - Error handling
   - Multi-tenant support

### 2. Multi-Model Semantic Layer Pattern

**Overview**: Supporting multiple semantic models for different business domains.

```
┌────────────────────── FastMCP Server ──────────────────────┐
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────┐ │
│  │   Sales Model   │  │ Marketing Model │  │  Finance   │ │
│  │  (Boring SL)    │  │   (Boring SL)   │  │   Model    │ │
│  └─────────────────┘  └─────────────────┘  └────────────┘ │
│           ↓                    ↓                   ↓        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────┐ │
│  │  Ibis (DuckDB)  │  │Ibis (BigQuery)  │  │Ibis (Snow) │ │
│  └─────────────────┘  └─────────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Implementation**:

```python
from fastmcp import FastMCP
from boring_semantic_layer import SemanticModel

# Sales semantic model
sales_model = SemanticModel(
    sales_table,
    dimensions=["product", "region", "customer_segment"],
    measures=["revenue", "units_sold", "avg_order_value"]
)

# Marketing semantic model
marketing_model = SemanticModel(
    campaigns_table,
    dimensions=["channel", "campaign_type", "audience"],
    measures=["impressions", "clicks", "conversions", "cac"]
)

# Finance semantic model
finance_model = SemanticModel(
    transactions_table,
    dimensions=["account", "department", "cost_center"],
    measures=["expenses", "budget_variance", "forecast"]
)

# MCP server exposing all models
mcp = FastMCP("Multi-Domain Analytics")

@mcp.tool()
def query_sales(dimensions: list[str], measures: list[str], filters: dict = None):
    """Query sales data"""
    return sales_model.query(dimensions=dimensions, measures=measures, filters=filters)

@mcp.tool()
def query_marketing(dimensions: list[str], measures: list[str], filters: dict = None):
    """Query marketing data"""
    return marketing_model.query(dimensions=dimensions, measures=measures, filters=filters)

@mcp.tool()
def query_finance(dimensions: list[str], measures: list[str], filters: dict = None):
    """Query finance data"""
    return finance_model.query(dimensions=dimensions, measures=measures, filters=filters)
```

**Benefits**:
- Domain separation (sales vs marketing vs finance)
- Different backends per domain (DuckDB for dev, BigQuery for prod)
- Team ownership of specific models
- Isolated changes and testing

### 3. Layered Caching Pattern

**Overview**: Multiple caching layers for optimal performance.

```
Claude Request
      ↓
[MCP Server Cache] ← In-memory cache for common queries
      ↓
[Semantic Layer Cache] ← Pre-computed aggregations
      ↓
[Ibis Query Cache] ← Compiled SQL cache
      ↓
[Database Cache] ← Database-native caching
      ↓
Raw Data
```

**Implementation**:

```python
from functools import lru_cache
from fastmcp import FastMCP, Context
import hashlib
import json

mcp = FastMCP("Cached Semantic Layer")

# MCP server-level cache (in-memory)
@lru_cache(maxsize=100)
def _cached_query(dimensions_tuple, measures_tuple, filters_json):
    dimensions = list(dimensions_tuple)
    measures = list(measures_tuple)
    filters = json.loads(filters_json) if filters_json else None
    return semantic_model.query(dimensions, measures, filters)

@mcp.tool()
def query_with_cache(
    dimensions: list[str],
    measures: list[str],
    filters: dict = None,
    ctx: Context = None
):
    """Query with multi-level caching"""
    # Create cache key
    cache_key = (
        tuple(sorted(dimensions)),
        tuple(sorted(measures)),
        json.dumps(filters, sort_keys=True) if filters else None
    )

    ctx.info(f"Cache key: {hashlib.md5(str(cache_key).encode()).hexdigest()}")

    # Check cache and return
    result = _cached_query(*cache_key)
    return result.to_dict(orient='records')
```

### 4. Proxy Pattern for Remote Semantic Layers

**Overview**: FastMCP proxying remote semantic layer services.

```
┌─────────────────────┐
│   Claude Desktop    │
└─────────────────────┘
          ↓
┌─────────────────────┐
│  Local FastMCP      │
│  Proxy Server       │
└─────────────────────┘
          ↓
    [Internet]
          ↓
┌─────────────────────┐
│  Remote Semantic    │
│  Layer Service      │
│  (Cube, dbt, etc.)  │
└─────────────────────┘
```

**Implementation**:

```python
from fastmcp import FastMCP
import httpx

# Proxy to remote Cube.dev semantic layer
cube_proxy = FastMCP("Cube.dev Proxy")

@cube_proxy.tool()
async def query_cube(dimensions: list[str], measures: list[str]):
    """Query remote Cube.dev semantic layer"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://cube-api.company.com/v1/load",
            json={
                "dimensions": dimensions,
                "measures": measures
            },
            headers={"Authorization": f"Bearer {CUBE_API_KEY}"}
        )
        return response.json()

# Proxy to remote dbt Semantic Layer
dbt_proxy = FastMCP("dbt Semantic Layer Proxy")

@dbt_proxy.tool()
async def query_dbt(metrics: list[str], group_by: list[str]):
    """Query remote dbt Semantic Layer"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://semantic-layer.getdbt.com/api/graphql",
            json={
                "query": f"""
                    query {{
                        metrics(names: {metrics}) {{
                            dimension({group_by}) {{
                                value
                            }}
                        }}
                    }}
                """
            },
            headers={"Authorization": f"Bearer {DBT_API_KEY}"}
        )
        return response.json()

# Main MCP server mounting proxies
main_mcp = FastMCP("Enterprise Analytics")
main_mcp.mount(cube_proxy)
main_mcp.mount(dbt_proxy)
```

**Benefits**:
- Works with existing semantic layer infrastructure
- No need to rewrite semantic models
- Adds authentication/logging layer
- Standardizes access through MCP

### 5. Hybrid Local + Remote Pattern

**Overview**: Local development with DuckDB, production with cloud warehouse.

```python
import os
from boring_semantic_layer import SemanticModel
import ibis

# Determine environment
ENV = os.getenv("ENVIRONMENT", "development")

if ENV == "development":
    # Local DuckDB for development
    conn = ibis.duckdb.connect()
    orders_table = conn.read_parquet("local_data/orders.parquet")
else:
    # Production BigQuery
    conn = ibis.bigquery.connect(project="company-prod")
    orders_table = conn.table("analytics.orders")

# Same semantic model definition works for both
orders_model = SemanticModel(
    orders_table,
    dimensions=["customer_id", "product", "region"],
    measures=["revenue", "units", "avg_order_value"]
)

# Same queries work in dev and prod
result = orders_model.query(
    dimensions=["region"],
    measures=["revenue"]
)
```

**Benefits**:
- Fast local iteration (DuckDB)
- Cost-effective development (no cloud charges)
- Production scalability (BigQuery/Snowflake)
- Identical business logic across environments

### 6. Evidence.dev + Semantic Layer Pattern

**Overview**: Combining Evidence.dev for visualization with semantic layer for metrics.

```
┌─────────────────────────────────────┐
│        Evidence.dev Reports          │
│     (SQL + Markdown + Components)    │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│      Semantic Layer (dbt/Cube)       │
│   (Metrics, dimensions, business     │
│            logic)                    │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│         Data Warehouse               │
│  (Snowflake, BigQuery, etc.)         │
└─────────────────────────────────────┘
```

**Evidence.dev Report Example**:

```markdown
# Sales Dashboard

```sql monthly_revenue
-- Query semantic layer metrics
SELECT
    metric_time AS month,
    revenue,
    units_sold
FROM {{ semantic_layer.query_metrics(
    metrics=['revenue', 'units_sold'],
    group_by=['metric_time'],
    grain='month'
) }}
```

<LineChart
    data={monthly_revenue}
    x=month
    y=revenue
    title="Monthly Revenue"
/>

<DataTable data={monthly_revenue}/>
```

**Benefits**:
- Evidence.dev handles visualization and UX
- Semantic layer ensures metric consistency
- Version control for reports (Git)
- Code-based workflow
- No metric duplication

### 7. Multi-Tenant Pattern

**Overview**: Single MCP server supporting multiple organizations with data isolation.

```python
from fastmcp import FastMCP, Context
from fastmcp.server.auth.providers.google import GoogleProvider

# Configure authentication
auth = GoogleProvider(
    client_id="...",
    client_secret="...",
    base_url="https://analytics.company.com"
)

mcp = FastMCP("Multi-Tenant Analytics", auth=auth)

def get_tenant_id(ctx: Context) -> str:
    """Extract tenant ID from authenticated user context"""
    user_email = ctx.auth.user.email
    # Map user to tenant (e.g., via domain or database lookup)
    return user_email.split("@")[1]  # Simple domain-based tenancy

@mcp.tool()
def query_data(dimensions: list[str], measures: list[str], ctx: Context):
    """Query data with automatic tenant isolation"""
    tenant_id = get_tenant_id(ctx)

    # Load tenant-specific semantic model
    tenant_model = load_semantic_model(tenant_id)

    # Apply tenant filter automatically
    result = tenant_model.query(
        dimensions=dimensions,
        measures=measures,
        filters={"tenant_id": {"eq": tenant_id}}
    )

    return result.to_dict(orient='records')
```

**Security Features**:
- Authentication required (OAuth)
- Automatic tenant isolation
- Row-level security enforcement
- Audit logging per tenant

### 8. Deepnote + MCP Pattern (Hypothetical)

**Overview**: Deepnote as interactive analysis environment with MCP for data access.

```
┌─────────────────────────────────────┐
│          Deepnote Notebook           │
│  (Python, R, SQL blocks + AI agent)  │
└─────────────────────────────────────┘
                 ↓
        MCP Protocol (hypothetical)
                 ↓
┌─────────────────────────────────────┐
│         FastMCP Server               │
│   (Semantic layer integration)       │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│     Boring Semantic Layer            │
└─────────────────────────────────────┘
```

**Potential Workflow**:

1. User asks Deepnote AI: "Show me monthly revenue by region"
2. Deepnote AI queries MCP server for available metrics
3. MCP returns dimensions/measures from semantic layer
4. Deepnote AI generates code block querying semantic layer
5. Results displayed in Deepnote visualization blocks
6. User iterates with follow-up questions

**Benefits**:
- Interactive exploration with semantic layer governance
- Notebook reproducibility
- AI-assisted analysis
- Version control through .deepnote YAML format

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Objective**: Establish basic semantic layer with local MCP server.

#### Week 1: Semantic Layer Setup

**Tasks**:
1. Install dependencies:
   ```bash
   pip install boring-semantic-layer[examples]
   pip install ibis-framework[duckdb]
   pip install fastmcp
   ```

2. Create initial semantic model:
   ```python
   # models/orders_model.py
   from boring_semantic_layer import to_semantic_table
   import ibis

   # Load data
   conn = ibis.duckdb.connect()
   orders = conn.read_parquet("data/orders.parquet")

   # Define semantic model
   orders_model = (
       to_semantic_table(orders, name="orders")
       .with_dimensions(
           customer_id=lambda t: t.customer_id,
           product=lambda t: t.product,
           region=lambda t: t.region,
           order_date=lambda t: t.order_date
       )
       .with_measures(
           revenue=lambda t: t.amount.sum(),
           order_count=lambda t: t.count(),
           avg_order_value=lambda t: t.amount.mean()
       )
       .with_time_dimension(
           time_dimension="order_date",
           time_format="%Y-%m-%d"
       )
   )
   ```

3. Test semantic model queries:
   ```python
   # Test basic query
   result = orders_model.query(
       dimensions=["region"],
       measures=["revenue", "order_count"]
   )
   print(result)

   # Test time-based query
   result = orders_model.query(
       time_dimensions=["order_date"],
       time_grain="month",
       measures=["revenue"]
   )
   print(result)
   ```

#### Week 2: MCP Server Implementation

**Tasks**:
1. Create basic MCP server:
   ```python
   # mcp_server.py
   from fastmcp import FastMCP
   from models.orders_model import orders_model
   import json

   mcp = FastMCP("Orders Analytics")

   @mcp.tool()
   def query_orders(
       dimensions: list[str],
       measures: list[str],
       filters: dict = None,
       time_grain: str = None
   ):
       """
       Query orders data with dimensions and measures.

       Available dimensions: customer_id, product, region, order_date
       Available measures: revenue, order_count, avg_order_value
       Time grains: day, week, month, quarter, year
       """
       kwargs = {
           "dimensions": dimensions,
           "measures": measures
       }

       if filters:
           kwargs["filters"] = filters

       if time_grain:
           kwargs["time_dimensions"] = ["order_date"]
           kwargs["time_grain"] = time_grain

       result = orders_model.query(**kwargs)
       return result.to_dict(orient='records')

   @mcp.tool()
   def get_available_metrics():
       """Get list of available dimensions and measures"""
       return {
           "dimensions": ["customer_id", "product", "region", "order_date"],
           "measures": ["revenue", "order_count", "avg_order_value"],
           "time_grains": ["day", "week", "month", "quarter", "year"]
       }

   if __name__ == "__main__":
       mcp.run()
   ```

2. Configure Claude Desktop:
   ```json
   {
     "mcpServers": {
       "orders_analytics": {
         "command": "python",
         "args": ["/path/to/project/mcp_server.py"]
       }
     }
   }
   ```

3. Test with Claude Desktop:
   - Restart Claude Desktop
   - Ask: "What are the available metrics in the orders dataset?"
   - Ask: "Show me monthly revenue by region"
   - Ask: "What was total revenue last quarter?"

**Deliverables**:
- ✅ Working semantic model with sample data
- ✅ Basic MCP server with query tools
- ✅ Claude Desktop integration configured
- ✅ Documentation of available metrics

### Phase 2: Enhancement (Weeks 3-4)

**Objective**: Add multiple models, caching, and better error handling.

#### Week 3: Multi-Model Support

**Tasks**:
1. Create additional semantic models:
   ```python
   # models/customers_model.py
   customers_model = (
       to_semantic_table(customers, name="customers")
       .with_dimensions(
           customer_id=lambda t: t.customer_id,
           segment=lambda t: t.segment,
           acquisition_channel=lambda t: t.acquisition_channel,
           signup_date=lambda t: t.signup_date
       )
       .with_measures(
           customer_count=lambda t: t.count(),
           ltv=lambda t: t.lifetime_value.sum(),
           avg_ltv=lambda t: t.lifetime_value.mean()
       )
   )

   # models/products_model.py
   products_model = (
       to_semantic_table(products, name="products")
       .with_dimensions(
           product_id=lambda t: t.product_id,
           category=lambda t: t.category,
           brand=lambda t: t.brand
       )
       .with_measures(
           product_count=lambda t: t.count(),
           avg_price=lambda t: t.price.mean(),
           total_inventory=lambda t: t.inventory.sum()
       )
   )
   ```

2. Extend MCP server:
   ```python
   @mcp.tool()
   def query_customers(dimensions: list[str], measures: list[str], filters: dict = None):
       """Query customer data"""
       result = customers_model.query(dimensions, measures, filters)
       return result.to_dict(orient='records')

   @mcp.tool()
   def query_products(dimensions: list[str], measures: list[str], filters: dict = None):
       """Query product data"""
       result = products_model.query(dimensions, measures, filters)
       return result.to_dict(orient='records')

   @mcp.tool()
   def list_available_models():
       """List all available semantic models and their schemas"""
       return {
           "orders": {
               "dimensions": ["customer_id", "product", "region", "order_date"],
               "measures": ["revenue", "order_count", "avg_order_value"]
           },
           "customers": {
               "dimensions": ["customer_id", "segment", "acquisition_channel", "signup_date"],
               "measures": ["customer_count", "ltv", "avg_ltv"]
           },
           "products": {
               "dimensions": ["product_id", "category", "brand"],
               "measures": ["product_count", "avg_price", "total_inventory"]
           }
       }
   ```

#### Week 4: Caching and Error Handling

**Tasks**:
1. Implement caching:
   ```python
   from functools import lru_cache
   import hashlib
   import json

   @lru_cache(maxsize=100)
   def _cached_query(model_name: str, dimensions_tuple, measures_tuple, filters_json):
       model = get_model(model_name)
       dimensions = list(dimensions_tuple)
       measures = list(measures_tuple)
       filters = json.loads(filters_json) if filters_json else None
       return model.query(dimensions, measures, filters)

   @mcp.tool()
   def query_with_cache(
       model: str,
       dimensions: list[str],
       measures: list[str],
       filters: dict = None,
       ctx: Context = None
   ):
       """Query with automatic caching"""
       cache_key = (
           model,
           tuple(sorted(dimensions)),
           tuple(sorted(measures)),
           json.dumps(filters, sort_keys=True) if filters else None
       )

       try:
           result = _cached_query(*cache_key)
           ctx.info(f"Query executed successfully (cached: {_cached_query.cache_info().hits > 0})")
           return result.to_dict(orient='records')
       except Exception as e:
           ctx.error(f"Query failed: {str(e)}")
           raise
   ```

2. Add comprehensive error handling:
   ```python
   @mcp.tool()
   def safe_query(
       model: str,
       dimensions: list[str],
       measures: list[str],
       filters: dict = None,
       ctx: Context = None
   ):
       """Query with validation and error handling"""
       # Validate model exists
       if model not in ["orders", "customers", "products"]:
           return {
               "error": f"Unknown model: {model}",
               "available_models": ["orders", "customers", "products"]
           }

       # Validate dimensions
       model_obj = get_model(model)
       available_dims = get_available_dimensions(model)
       invalid_dims = [d for d in dimensions if d not in available_dims]
       if invalid_dims:
           return {
               "error": f"Invalid dimensions: {invalid_dims}",
               "available_dimensions": available_dims
           }

       # Execute query with error handling
       try:
           result = model_obj.query(dimensions, measures, filters)
           return {
               "success": True,
               "data": result.to_dict(orient='records'),
               "row_count": len(result)
           }
       except Exception as e:
           ctx.error(f"Query execution failed: {str(e)}")
           return {
               "error": str(e),
               "model": model,
               "dimensions": dimensions,
               "measures": measures
           }
   ```

**Deliverables**:
- ✅ Multiple semantic models (orders, customers, products)
- ✅ Query caching implementation
- ✅ Comprehensive error handling
- ✅ Validation of user inputs

### Phase 3: Production Features (Weeks 5-6)

**Objective**: Add authentication, logging, and production deployment.

#### Week 5: Authentication and Authorization

**Tasks**:
1. Implement OAuth authentication:
   ```python
   from fastmcp.server.auth.providers.google import GoogleProvider

   auth = GoogleProvider(
       client_id=os.getenv("GOOGLE_CLIENT_ID"),
       client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
       base_url=os.getenv("BASE_URL", "http://localhost:8000")
   )

   mcp = FastMCP("Secure Analytics", auth=auth)
   ```

2. Add role-based access control:
   ```python
   def get_user_role(ctx: Context) -> str:
       """Determine user role from authentication context"""
       email = ctx.auth.user.email
       if email.endswith("@company.com"):
           return "employee"
       elif email in ADMIN_EMAILS:
           return "admin"
       else:
           return "guest"

   @mcp.tool()
   def query_with_rbac(
       model: str,
       dimensions: list[str],
       measures: list[str],
       ctx: Context = None
   ):
       """Query with role-based access control"""
       role = get_user_role(ctx)

       # Check if user can access this model
       if model == "finance" and role not in ["admin"]:
           return {"error": "Unauthorized: admin access required"}

       # Apply row-level security based on role
       filters = {}
       if role == "employee":
           filters["department"] = {"eq": ctx.auth.user.department}

       result = get_model(model).query(dimensions, measures, filters)
       return result.to_dict(orient='records')
   ```

3. Add audit logging:
   ```python
   import logging
   from datetime import datetime

   audit_logger = logging.getLogger("audit")

   @mcp.tool()
   def query_with_audit(
       model: str,
       dimensions: list[str],
       measures: list[str],
       ctx: Context = None
   ):
       """Query with audit logging"""
       # Log query
       audit_logger.info({
           "timestamp": datetime.utcnow().isoformat(),
           "user": ctx.auth.user.email,
           "model": model,
           "dimensions": dimensions,
           "measures": measures,
           "ip_address": ctx.request.client.host
       })

       # Execute query
       result = get_model(model).query(dimensions, measures)

       # Log results
       audit_logger.info({
           "timestamp": datetime.utcnow().isoformat(),
           "user": ctx.auth.user.email,
           "row_count": len(result),
           "success": True
       })

       return result.to_dict(orient='records')
   ```

#### Week 6: Production Deployment

**Tasks**:
1. Migrate from DuckDB to production warehouse:
   ```python
   import os

   ENV = os.getenv("ENVIRONMENT", "development")

   if ENV == "development":
       conn = ibis.duckdb.connect()
       orders = conn.read_parquet("data/orders.parquet")
   elif ENV == "staging":
       conn = ibis.bigquery.connect(project="company-staging")
       orders = conn.table("analytics.orders")
   else:  # production
       conn = ibis.snowflake.connect(
           user=os.getenv("SNOWFLAKE_USER"),
           password=os.getenv("SNOWFLAKE_PASSWORD"),
           account=os.getenv("SNOWFLAKE_ACCOUNT"),
           warehouse=os.getenv("SNOWFLAKE_WAREHOUSE")
       )
       orders = conn.table("analytics.orders")

   # Same semantic model definition works across all environments
   orders_model = to_semantic_table(orders, name="orders")...
   ```

2. Deploy with Docker:
   ```dockerfile
   # Dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install -r requirements.txt

   COPY . .

   ENV ENVIRONMENT=production

   CMD ["python", "mcp_server.py"]
   ```

3. Configure production deployment:
   ```yaml
   # docker-compose.yml
   version: '3.8'
   services:
     mcp_server:
       build: .
       ports:
         - "8000:8000"
       environment:
         - ENVIRONMENT=production
         - SNOWFLAKE_USER=${SNOWFLAKE_USER}
         - SNOWFLAKE_PASSWORD=${SNOWFLAKE_PASSWORD}
         - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
         - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
       restart: always
   ```

4. Setup monitoring:
   ```python
   from prometheus_client import Counter, Histogram

   query_counter = Counter('mcp_queries_total', 'Total queries', ['model', 'user'])
   query_duration = Histogram('mcp_query_duration_seconds', 'Query duration')

   @mcp.tool()
   @query_duration.time()
   def monitored_query(model: str, dimensions: list[str], measures: list[str], ctx: Context = None):
       """Query with monitoring"""
       query_counter.labels(model=model, user=ctx.auth.user.email).inc()

       result = get_model(model).query(dimensions, measures)
       return result.to_dict(orient='records')
   ```

**Deliverables**:
- ✅ OAuth authentication implemented
- ✅ Role-based access control
- ✅ Audit logging
- ✅ Production database connection
- ✅ Docker deployment
- ✅ Monitoring and observability

### Phase 4: Advanced Features (Weeks 7-8)

**Objective**: Integration with Evidence.dev, advanced caching, and AI enhancements.

#### Week 7: Evidence.dev Integration

**Tasks**:
1. Setup Evidence.dev project:
   ```bash
   npm install -g @evidence-dev/cli
   npx degit evidence-dev/template analytics_reports
   cd analytics_reports
   npm install
   ```

2. Configure semantic layer connection:
   ```yaml
   # sources/semantic_layer.yaml
   name: semantic_layer
   type: http
   connection:
     base_url: http://localhost:8000
     headers:
       Authorization: Bearer ${SEMANTIC_LAYER_TOKEN}
   ```

3. Create Evidence.dev reports using semantic layer:
   ```markdown
   # Monthly Revenue Dashboard

   ```sql monthly_revenue
   SELECT * FROM query_model(
     model := 'orders',
     dimensions := ARRAY['order_date'],
     measures := ARRAY['revenue', 'order_count'],
     time_grain := 'month'
   )
   ```

   <LineChart
       data={monthly_revenue}
       x=order_date
       y=revenue
       title="Monthly Revenue Trend"
   />

   <BigValue
       data={monthly_revenue}
       value=revenue
       title="Total Revenue"
   />
   ```

#### Week 8: Advanced Caching and AI Features

**Tasks**:
1. Implement materialized views:
   ```python
   from apscheduler.schedulers.background import BackgroundScheduler

   # Pre-compute common aggregations
   scheduler = BackgroundScheduler()

   def materialize_common_queries():
       """Pre-compute and cache common queries"""
       common_queries = [
           ("orders", ["region"], ["revenue"], None),
           ("orders", ["product"], ["order_count"], None),
           ("customers", ["segment"], ["ltv"], None)
       ]

       for model, dims, measures, filters in common_queries:
           result = get_model(model).query(dims, measures, filters)
           cache_key = f"{model}:{':'.join(dims)}:{':'.join(measures)}"
           redis_client.set(cache_key, result.to_json(), ex=3600)

   # Run every hour
   scheduler.add_job(materialize_common_queries, 'interval', hours=1)
   scheduler.start()
   ```

2. Add AI-powered query suggestions:
   ```python
   @mcp.tool()
   async def suggest_analysis(question: str, ctx: Context):
       """Get AI suggestions for how to answer a business question"""
       # Use Claude to suggest relevant dimensions and measures
       suggestion = await ctx.sample(f"""
       Given this business question: "{question}"

       Available models and their schemas:
       {json.dumps(list_available_models(), indent=2)}

       Suggest:
       1. Which model(s) to query
       2. Which dimensions to use
       3. Which measures to calculate
       4. Any useful filters

       Respond in JSON format.
       """)

       return json.loads(suggestion)
   ```

3. Implement query optimization:
   ```python
   @mcp.tool()
   def optimize_query(
       model: str,
       dimensions: list[str],
       measures: list[str],
       filters: dict = None,
       ctx: Context = None
   ):
       """Automatically optimize query performance"""
       # Check if dimensions create a large cardinality
       cardinality_estimate = estimate_cardinality(model, dimensions)

       if cardinality_estimate > 1000000:
           ctx.info(f"High cardinality detected ({cardinality_estimate:,} rows). Adding sampling.")
           # Add sampling for high cardinality queries
           return get_model(model).query(
               dimensions, measures, filters
           ).sample(fraction=0.1)

       # Use pre-computed materialization if available
       cache_key = f"{model}:{':'.join(sorted(dimensions))}:{':'.join(sorted(measures))}"
       cached = redis_client.get(cache_key)
       if cached:
           ctx.info("Using pre-computed materialization")
           return json.loads(cached)

       # Normal query
       return get_model(model).query(dimensions, measures, filters).to_dict(orient='records')
   ```

**Deliverables**:
- ✅ Evidence.dev integration with semantic layer
- ✅ Materialized view caching
- ✅ AI-powered query suggestions
- ✅ Automatic query optimization

### Phase 5: Ecosystem Integration (Weeks 9-10)

**Objective**: Integrate with broader ecosystem (Deepnote, Jupyter, BI tools).

#### Week 9: Notebook Integration

**Tasks**:
1. Create Python SDK for notebook usage:
   ```python
   # sdk/semantic_layer_client.py
   from fastmcp import Client
   import pandas as pd

   class SemanticLayerClient:
       def __init__(self, server_url="http://localhost:8000"):
           self.server_url = server_url

       async def query(self, model: str, dimensions: list[str], measures: list[str], filters: dict = None):
           """Query semantic layer from notebook"""
           async with Client(self.server_url) as client:
               result = await client.call_tool("query_with_cache", {
                   "model": model,
                   "dimensions": dimensions,
                   "measures": measures,
                   "filters": filters
               })
               return pd.DataFrame(result)

       async def list_models(self):
           """List available models"""
           async with Client(self.server_url) as client:
               return await client.call_tool("list_available_models", {})
   ```

2. Create Jupyter magic commands:
   ```python
   # jupyter_extension/semantic_layer_magic.py
   from IPython.core.magic import register_line_magic, register_cell_magic
   import asyncio

   sl_client = SemanticLayerClient()

   @register_line_magic
   def sl_query(line):
       """
       %sl_query orders revenue by region
       """
       parts = line.split()
       model = parts[0]
       measures = [parts[1]]
       dimensions = [parts[3]] if len(parts) > 3 else []

       result = asyncio.run(sl_client.query(model, dimensions, measures))
       return result

   @register_cell_magic
   def semantic_layer(line, cell):
       """
       %%semantic_layer
       model: orders
       dimensions: [region, product]
       measures: [revenue, order_count]
       """
       import yaml
       config = yaml.safe_load(cell)
       result = asyncio.run(sl_client.query(
           config['model'],
           config['dimensions'],
           config['measures'],
           config.get('filters')
       ))
       return result
   ```

3. Deepnote integration (hypothetical):
   ```python
   # deepnote_integration.py
   # This would require Deepnote API access
   from deepnote_api import DeepnoteClient

   @mcp.tool()
   def create_deepnote_analysis(question: str, ctx: Context):
       """Create Deepnote notebook analyzing a question"""
       # Get AI suggestion for analysis approach
       suggestion = suggest_analysis(question)

       # Create Deepnote notebook with blocks
       notebook = DeepnoteClient().create_notebook(f"Analysis: {question}")

       # Add markdown block with question
       notebook.add_block("markdown", f"# Analysis: {question}")

       # Add code block with query
       notebook.add_block("code", f"""
       from semantic_layer_client import SemanticLayerClient
       sl = SemanticLayerClient()

       result = await sl.query(
           model='{suggestion['model']}',
           dimensions={suggestion['dimensions']},
           measures={suggestion['measures']}
       )
       result
       """)

       # Add visualization block
       notebook.add_block("visualization", {
           "type": "bar",
           "data": "result",
           "x": suggestion['dimensions'][0],
           "y": suggestion['measures'][0]
       })

       return notebook.url
   ```

#### Week 10: BI Tool Integration

**Tasks**:
1. Create REST API endpoint for BI tools:
   ```python
   from fastapi import FastAPI
   from fastapi.middleware.cors import CORSMiddleware

   app = FastAPI()
   app.add_middleware(CORSMiddleware, allow_origins=["*"])

   @app.post("/api/query")
   async def query_endpoint(
       model: str,
       dimensions: list[str],
       measures: list[str],
       filters: dict = None
   ):
       """REST endpoint for BI tools (Tableau, Power BI, etc.)"""
       result = get_model(model).query(dimensions, measures, filters)
       return {
           "data": result.to_dict(orient='records'),
           "metadata": {
               "row_count": len(result),
               "dimensions": dimensions,
               "measures": measures
           }
       }

   @app.get("/api/models")
   async def models_endpoint():
       """List available models for BI tool configuration"""
       return list_available_models()
   ```

2. Create Tableau Web Data Connector:
   ```javascript
   // tableau_wdc.js
   (function() {
       var myConnector = tableau.makeConnector();

       myConnector.getSchema = function(schemaCallback) {
           // Fetch schema from semantic layer
           fetch('http://localhost:8000/api/models')
               .then(response => response.json())
               .then(models => {
                   var cols = models.orders.dimensions.concat(models.orders.measures)
                       .map(field => ({
                           id: field,
                           alias: field,
                           dataType: tableau.dataTypeEnum.string
                       }));

                   var tableSchema = {
                       id: "orders",
                       alias: "Orders Data",
                       columns: cols
                   };

                   schemaCallback([tableSchema]);
               });
       };

       myConnector.getData = function(table, doneCallback) {
           // Fetch data from semantic layer
           fetch('http://localhost:8000/api/query', {
               method: 'POST',
               headers: {'Content-Type': 'application/json'},
               body: JSON.stringify({
                   model: 'orders',
                   dimensions: ['region', 'product'],
                   measures: ['revenue', 'order_count']
               })
           })
           .then(response => response.json())
           .then(data => {
               table.appendRows(data.data);
               doneCallback();
           });
       };

       tableau.registerConnector(myConnector);
   })();
   ```

3. Create GraphQL API for flexible querying:
   ```python
   from ariadne import QueryType, make_executable_schema
   from ariadne.asgi import GraphQL

   type_defs = """
       type Query {
           queryModel(
               model: String!,
               dimensions: [String!]!,
               measures: [String!]!,
               filters: JSON
           ): QueryResult!

           listModels: [Model!]!
       }

       type QueryResult {
           data: [JSON!]!
           rowCount: Int!
       }

       type Model {
           name: String!
           dimensions: [String!]!
           measures: [String!]!
       }
   """

   query = QueryType()

   @query.field("queryModel")
   def resolve_query_model(_, info, model, dimensions, measures, filters=None):
       result = get_model(model).query(dimensions, measures, filters)
       return {
           "data": result.to_dict(orient='records'),
           "rowCount": len(result)
       }

   @query.field("listModels")
   def resolve_list_models(_, info):
       return list_available_models()

   schema = make_executable_schema(type_defs, query)
   graphql_app = GraphQL(schema)
   ```

**Deliverables**:
- ✅ Python SDK for notebook usage
- ✅ Jupyter magic commands
- ✅ REST API for BI tools
- ✅ Tableau Web Data Connector
- ✅ GraphQL API
- ✅ Deepnote integration concept

### Success Metrics

**Technical Metrics**:
- Query response time < 2 seconds (P95)
- Cache hit rate > 70%
- API uptime > 99.5%
- Authentication success rate > 99%

**Business Metrics**:
- Number of active users
- Queries per day
- Unique models accessed
- Integration adoption rate

**Quality Metrics**:
- Zero SQL injection vulnerabilities
- 100% metric definition consistency
- < 1% query error rate
- Complete audit trail coverage

---

## References

### Primary Sources

**Semantic Layer Guides**:
- Rasmus Engelbrecht - Practical Guide to Semantic Layers (Part 1): https://rasmusengelbrecht.substack.com/p/practical-guide-to-semantic-layers
- Rasmus Engelbrecht - Practical Guide to Semantic Layers (Part 2 - MCP): https://rasmusengelbrecht.substack.com/p/practical-guide-to-semantic-layers-34d

**Boring Semantic Layer**:
- GitHub Repository: https://github.com/boringdata/boring-semantic-layer
- PyPI Package: https://pypi.org/project/boring-semantic-layer/
- Julien Hurault - Launching BSL: https://juhache.substack.com/p/the-boring-semantic-layer
- Julien Hurault - BSL + MCP: https://juhache.substack.com/p/boring-semantic-layer-mcp

**Ibis Project**:
- Official Website: https://ibis-project.org/
- GitHub Repository: https://github.com/ibis-project/ibis
- Documentation: https://ibis-project.org/docs/

**Model Context Protocol**:
- Official Announcement: https://www.anthropic.com/news/model-context-protocol
- Documentation: https://modelcontextprotocol.io/
- GitHub - MCP Servers: https://github.com/modelcontextprotocol/servers
- GitHub - Python SDK: https://github.com/modelcontextprotocol/python-sdk

**FastMCP**:
- GitHub Repository: https://github.com/jlowin/fastmcp
- Documentation: https://gofastmcp.com
- PyPI Package: https://pypi.org/project/fastmcp/

**Evidence.dev**:
- Official Website: https://evidence.dev/
- GitHub Repository: https://github.com/evidence-dev/evidence
- Documentation: https://docs.evidence.dev/

**Deepnote**:
- Official Website: https://deepnote.com/
- GitHub Repository: https://github.com/deepnote/deepnote
- Documentation: https://docs.deepnote.com/

### Secondary Sources

**Semantic Layer Architecture**:
- MotherDuck Blog - Why Semantic Layers Matter: https://motherduck.com/blog/semantic-layer-duckdb-tutorial/
- Cube.dev - Unlocking Universal Data Access for AI: https://cube.dev/blog/unlocking-universal-data-access-for-ai-with-anthropics-model-context

**Tools & Frameworks**:
- dbt Semantic Layer: https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-semantic-layer
- Cube.dev: https://cube.dev/
- Malloy: https://github.com/malloydata/malloy
- AtScale: https://www.atscale.com/

**Best Practices**:
- dbt - Building Semantic Models: https://docs.getdbt.com/best-practices/how-we-build-our-metrics/semantic-layer-3-build-semantic-models
- Databricks - Semantic Layer in Modern Data Analytics: https://www.databricks.com/glossary/semantic-layer

### Community Resources

**GitHub Topics**:
- #semantic-layer: https://github.com/topics/semantic-layer
- #model-context-protocol: https://github.com/topics/model-context-protocol
- #ibis: https://github.com/topics/ibis

**Articles & Tutorials**:
- Firecrawl - How to Build MCP Servers in Python: https://www.firecrawl.dev/blog/fastmcp-tutorial-building-mcp-servers-python
- DataCamp - Building MCP Server and Client with FastMCP: https://www.datacamp.com/tutorial/building-mcp-server-client-fastmcp
- MCPcat - Complete Guide to FastMCP: https://mcpcat.io/guides/building-mcp-server-python-fastmcp/

---

## Appendices

### Appendix A: Glossary

**Semantic Layer**: A business representation layer that sits between raw data and analytics tools, translating technical database structures into business-friendly metrics and dimensions.

**MCP (Model Context Protocol)**: Open standard protocol for connecting AI assistants to external data sources and tools in a standardized, secure way.

**Ibis**: Portable Python dataframe library that provides a unified API for querying across 20+ database backends.

**Boring Semantic Layer**: Lightweight, Python-native semantic layer built on Ibis, designed for simplicity and MCP integration.

**FastMCP**: Production-ready Python framework for building MCP servers with advanced features like authentication, proxying, and composition.

**Evidence.dev**: Business intelligence as code platform enabling data teams to build reports using SQL, markdown, and version control.

**Deepnote**: Modern notebook platform (Jupyter successor) with AI integration and collaborative features.

**Dimension**: Categorical attribute used for slicing data (e.g., region, product, customer_segment).

**Measure**: Quantitative metric calculated through aggregation (e.g., revenue, count, average).

**Tool (MCP)**: Function that an LLM can execute, similar to a POST endpoint.

**Resource (MCP)**: Read-only data source accessible via URI, similar to a GET endpoint.

**Prompt (MCP)**: Reusable message template for LLM interactions.

### Appendix B: Quick Start Commands

```bash
# Install dependencies
pip install boring-semantic-layer[examples]
pip install ibis-framework[duckdb]
pip install fastmcp

# Create semantic model
python -c "from boring_semantic_layer import to_semantic_table; import ibis; conn = ibis.duckdb.connect(); orders = conn.read_parquet('data.parquet'); model = to_semantic_table(orders, 'orders')"

# Run MCP server
python mcp_server.py

# Test with FastMCP client
python -c "from fastmcp import Client; import asyncio; asyncio.run(Client('http://localhost:8000').list_tools())"

# Configure Claude Desktop
# Edit: ~/Library/Application Support/Claude/claude_desktop_config.json
# Add MCP server configuration
```

### Appendix C: Configuration Templates

**Claude Desktop MCP Configuration**:
```json
{
  "mcpServers": {
    "semantic_layer": {
      "command": "python",
      "args": ["/path/to/mcp_server.py"]
    }
  }
}
```

**Environment Variables**:
```bash
# Development
ENVIRONMENT=development

# Production
ENVIRONMENT=production
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account

# Authentication
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret

# MCP Server
MCP_HOST=0.0.0.0
MCP_PORT=8000
```

**Docker Compose**:
```yaml
version: '3.8'
services:
  mcp_server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
    env_file:
      - .env
    restart: always
```

---

**End of Research Document**

*This research document provides a comprehensive foundation for building AI analyst systems that integrate semantic layers with Claude Desktop via MCP. All architectural patterns, code examples, and implementation guidance are based on current best practices as of November 2025.*
