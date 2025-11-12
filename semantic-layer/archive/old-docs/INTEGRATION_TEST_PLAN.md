# Claude Desktop Integration Test Plan

## Pre-Test Setup ✅
- [x] Backed up existing Claude Desktop config
- [x] Added AI Analyst MCP server to configuration
- [x] Validated JSON configuration syntax
- [x] Verified MCP server starts correctly
- [ ] **NEXT: Restart Claude Desktop completely**

## Test Sequence

### Test 1: Basic MCP Tool Discovery
**Objective**: Verify Claude Desktop can see the AI Analyst tools

**Commands to try**:
```
What MCP tools are available?
```

**Expected**: Should see AI Analyst tools listed: `list_models`, `query_model`, `suggest_analysis`, etc.

---

### Test 2: Semantic Model Listing
**Objective**: Test the execution-first pattern with model discovery

**Commands to try**:
```
List the available data models

What semantic models do we have?
```

**Expected**:
- Should execute `list_models` tool
- Show 3 models: users, events, engagement
- Display model descriptions and metrics counts

---

### Test 3: Basic Data Query
**Objective**: Test query building, execution, and interpretation

**Commands to try**:
```
What's our conversion rate by plan type?

Show me user distribution by plan type
```

**Expected**:
- Should execute `query_model` tool with users model
- Generate and run SQL query
- Return results with statistical validation
- Provide natural language interpretation
- Include business context (vs industry benchmarks)

---

### Test 4: Statistical Analysis
**Objective**: Verify automatic statistical testing

**Commands to try**:
```
Is the difference in conversion rates by plan type statistically significant?

Test if engagement varies significantly by plan type
```

**Expected**:
- Should execute `test_significance` tool
- Run appropriate statistical test (ANOVA, chi-square, etc.)
- Report p-values and effect sizes
- Interpret practical significance

---

### Test 5: Analysis Suggestions
**Objective**: Test intelligent next-question recommendations

**Commands to try**:
```
What analysis should I do next?

Suggest follow-up questions based on the conversion rate results
```

**Expected**:
- Should execute `suggest_analysis` tool
- Provide 3-4 logical next questions
- Include reasoning for each suggestion
- Be contextually relevant to previous analysis

---

### Test 6: Complex Query (Multi-Model)
**Objective**: Test more complex analysis across models

**Commands to try**:
```
Which features are most popular among high-converting users?

How does feature usage correlate with plan type?
```

**Expected**:
- Should use events model with user joins
- Generate complex SQL with proper joins
- Handle cross-model relationships
- Provide insights with statistical validation

---

### Test 7: Execution-First Validation
**Objective**: Verify no fabrication occurs

**Commands to try**:
```
What's the monthly churn rate trend?
```

**Expected**:
- Should only make claims based on actual query results
- If data doesn't exist, should say so clearly
- No hallucinated numbers or fake trends
- Clear error messages if queries fail

---

### Test 8: Health Check
**Objective**: Test system monitoring

**Commands to try**:
```
Check the health of the AI Analyst system

Is the database connection working?
```

**Expected**:
- Should execute `health_check` tool
- Show database status and file size
- Report number of loaded models
- Indicate if system is healthy

---

## Success Criteria

### ✅ Tool Discovery
- [ ] All 7 MCP tools visible in Claude Desktop
- [ ] Tools respond without errors
- [ ] FastMCP server connection established

### ✅ Execution-First Pattern
- [ ] All queries execute against real database
- [ ] No fabricated numbers or results
- [ ] Clear error handling when queries fail

### ✅ Statistical Rigor
- [ ] Automatic significance testing when comparing groups
- [ ] Sample size validation with warnings
- [ ] Effect size reporting (small/medium/large)

### ✅ Natural Language
- [ ] Concise, natural observations
- [ ] Statistical evidence included (p-values, sample sizes)
- [ ] Business context with benchmarks

### ✅ Analysis Workflow
- [ ] Logical question suggestions
- [ ] Progressive exploration capability
- [ ] Context-aware recommendations

## Troubleshooting

### MCP Server Not Loading
1. Check Claude Desktop logs/console
2. Verify JSON configuration syntax
3. Test server starts manually: `uv run python test_mcp_server.py`
4. Check file paths in configuration

### Tools Not Working
1. Look for error messages in responses
2. Test individual functions: `uv run python -c "from mcp_server.server import semantic_manager; import asyncio; asyncio.run(semantic_manager.health_check())"`
3. Verify database file exists: `ls data/analytics.duckdb`

### Query Errors
1. Check SQL generation with debug output
2. Verify semantic model definitions
3. Test direct database queries

## Recovery Plan

If anything breaks:
```bash
# Restore original config
cp ~/Library/Application\ Support/Claude/claude_desktop_config.backup.*.json ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Restart Claude Desktop
```

---

**Ready to begin testing!** Please restart Claude Desktop and then try Test 1.