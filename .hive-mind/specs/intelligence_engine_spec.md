# IntelligenceEngine - SPARC Specification

**Component**: `IntelligenceEngine` (mcp_server/intelligence_layer.py)
**Status**: ❌ FAILING - Missing `interpret_query_result()` and `generate_analysis_suggestions()` methods
**Priority**: CRITICAL - Blocks NLG and end-to-end integration

---

## S - Specification

### Problem Statement

The test expects a simplified `interpret_query_result()` method that takes result, dimensions, and measures directly, but the implementation has a more complex `generate_interpretation()` method that requires a full query_info dict.

Additionally, tests expect `generate_analysis_suggestions()` but implementation has `suggest_next_questions()` and `suggest_analysis_paths()`.

### Required API Contracts

#### Method 1: `interpret_query_result()`

```python
async def interpret_query_result(
    self,
    result: Dict[str, Any],
    dimensions: List[str] = [],
    measures: List[str] = []
) -> str:
    """
    Generate natural language interpretation of query results.

    Args:
        result: Query execution result containing data, execution_time_ms, etc.
        dimensions: List of dimension names used in query
        measures: List of measure names used in query

    Returns:
        Natural language interpretation string (concise, authentic observations)

    Examples:
        >>> result = {"data": [{"plan": "pro", "users": 100}, {"plan": "free", "users": 50}]}
        >>> await engine.interpret_query_result(result, ["plan"], ["users"])
        "2 results | Pro 2x higher users than Free"
    """
    pass
```

**Type Signature**:
- `result: Dict[str, Any]` - Query result with keys: data, execution_time_ms, row_count, columns
- `dimensions: List[str]` - Dimension column names (default: [])
- `measures: List[str]` - Measure column names (default: [])
- **Returns**: `str` - Concise natural language interpretation

**Required Behavior**:
1. MUST work with real executed data only (execution-first pattern)
2. MUST generate concise observations (not verbose academic language)
3. MUST handle empty results gracefully
4. SHOULD include statistical context when available
5. SHOULD follow Mercury notebook style (shortest natural phrasing)

---

#### Method 2: `generate_analysis_suggestions()`

```python
async def generate_analysis_suggestions(
    self,
    current_result: Optional[Dict[str, Any]] = None,
    context: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Generate suggested next analysis steps based on current result.

    Args:
        current_result: Current query result (optional)
        context: Contextual information about analysis state (optional)

    Returns:
        List of suggestion dicts with keys: question, reason

    Examples:
        >>> suggestions = await engine.generate_analysis_suggestions(
        ...     current_result={"data": [...]},
        ...     context="conversion_analysis"
        ... )
        >>> suggestions[0]
        {"question": "How does conversion vary by industry?", "reason": "Drill into segments"}
    """
    pass
```

**Type Signature**:
- `current_result: Optional[Dict[str, Any]]` - Current query result
- `context: Optional[str]` - Analysis context string
- **Returns**: `List[Dict[str, str]]` - List of suggestions with question and reason

**Required Behavior**:
1. MUST return list of dicts with "question" and "reason" keys
2. SHOULD be context-aware based on current result patterns
3. SHOULD suggest statistical validation for comparisons
4. SHOULD suggest drill-downs for grouped data
5. MUST return at least 1 suggestion (fallback to general suggestions)

---

### Integration Points

**Existing Methods to Preserve**:
- `generate_interpretation()` - Keep for internal use, more complex signature
- `suggest_next_questions()` - Keep for internal use
- `suggest_analysis_paths()` - Keep for internal use
- `interpret_statistical_results()` - Keep, working correctly

**New Methods Should**:
- Delegate to existing implementation methods
- Adapt parameters between test API and internal API
- Bridge the gap between test expectations and current implementation

---

## P - Pseudocode

### `interpret_query_result()` Algorithm

```
FUNCTION interpret_query_result(result, dimensions, measures):
    # Convert simplified parameters to internal format
    query_info = {
        "dimensions": dimensions,
        "measures": measures,
        "model": extract_model_from_result(result) OR "unknown"
    }

    # Delegate to existing generate_interpretation method
    interpretation = AWAIT generate_interpretation(
        result=result,
        query_info=query_info,
        validation=None,  # Optional, can be added later
        statistical_analysis=None  # Optional, can be added later
    )

    RETURN interpretation
END FUNCTION
```

**Complexity**: O(n) where n = number of rows in result
**Performance**: <10ms for typical result sizes (10-100 rows)

### `generate_analysis_suggestions()` Algorithm

```
FUNCTION generate_analysis_suggestions(current_result, context):
    # Extract dimensions and measures from current result if available
    IF current_result IS NOT None:
        dimensions = extract_dimensions_from_result(current_result)
        measures = extract_measures_from_result(current_result)
    ELSE:
        dimensions = []
        measures = []
    END IF

    # Try suggest_next_questions first (most specific)
    IF current_result IS NOT None:
        suggestions = AWAIT suggest_next_questions(
            result=current_result,
            context=context OR "",
            current_dimensions=dimensions,
            current_measures=measures
        )

        # Convert format if needed
        formatted_suggestions = [
            {
                "question": s.get("question", ""),
                "reason": s.get("reason", "")
            }
            FOR s IN suggestions
        ]

        IF LENGTH(formatted_suggestions) > 0:
            RETURN formatted_suggestions
        END IF
    END IF

    # Fallback to suggest_analysis_paths (more general)
    suggestions = AWAIT suggest_analysis_paths(
        current_result=current_result,
        context=context,
        model=None
    )

    # Format and return
    formatted_suggestions = [
        {
            "question": s.get("question", ""),
            "reason": s.get("reason", "")
        }
        FOR s IN suggestions
    ]

    RETURN formatted_suggestions[:5]  # Limit to 5 suggestions
END FUNCTION
```

**Complexity**: O(n) where n = number of data rows
**Performance**: <20ms typical

---

## A - Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────┐
│         IntelligenceEngine (Public API)         │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌────────────────────────────────────────┐    │
│  │  New Test-Compatible Methods           │    │
│  │                                         │    │
│  │  • interpret_query_result() ────┐      │    │
│  │                                  │      │    │
│  │  • generate_analysis_suggestions()     │    │
│  │                            │     │      │    │
│  └────────────────────────────┼─────┼──────┘    │
│                               │     │           │
│                               ▼     ▼           │
│  ┌────────────────────────────────────────┐    │
│  │  Existing Implementation Methods       │    │
│  │                                         │    │
│  │  • generate_interpretation()           │    │
│  │  • suggest_next_questions()            │    │
│  │  • suggest_analysis_paths()            │    │
│  │  • interpret_statistical_results()     │    │
│  │  • _get_business_context()             │    │
│  └────────────────────────────────────────┘    │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Integration Pattern

**Adapter Pattern**: New methods act as adapters between test API and existing implementation

```
Test API (Simple)  →  Adapter Methods  →  Existing API (Complex)
   ├─ result           ├─ Parameter           ├─ query_info dict
   ├─ dimensions       │   transformation     ├─ validation dict
   └─ measures         └─ Delegation           └─ statistical_analysis
```

### Dependencies

**Required Imports** (already in file):
- `datetime` - For timestamp handling
- `typing.Dict, List, Any, Optional` - Type hints
- No new dependencies required

**Internal Dependencies**:
- Existing `generate_interpretation()` method
- Existing `suggest_next_questions()` method
- Existing `suggest_analysis_paths()` method

**External Dependencies**:
- None (methods are self-contained within IntelligenceEngine)

---

## R - Refinement

### Edge Cases

1. **Empty Result Data**
   ```python
   result = {"data": [], "row_count": 0}
   # Expected: "No data returned for this query."
   ```

2. **Missing Dimensions/Measures**
   ```python
   result = {"data": [{"col1": 100}]}
   dimensions = []
   measures = []
   # Expected: Basic count-based interpretation
   ```

3. **Single Row Result**
   ```python
   result = {"data": [{"total": 12345}]}
   # Expected: "Single result | total: 12.3K"
   ```

4. **Query Error in Result**
   ```python
   result = {"error": "SQL syntax error", "data": []}
   # Expected: "Query failed: SQL syntax error"
   ```

5. **Null/None Values in Data**
   ```python
   result = {"data": [{"plan": None, "users": 100}]}
   # Expected: Handle gracefully, skip null groups
   ```

### Error Handling

```python
async def interpret_query_result(self, result, dimensions=[], measures=[]):
    try:
        # Check for error in result
        if result.get("error"):
            return f"Query failed: {result['error']}"

        # Check for empty data
        data = result.get("data", [])
        if not data:
            return "No data returned for this query."

        # Build query_info for internal method
        query_info = {
            "dimensions": dimensions or [],
            "measures": measures or [],
            "model": "unknown"  # Can be enhanced later
        }

        # Delegate to existing method (already handles edge cases)
        interpretation = await self.generate_interpretation(
            result=result,
            query_info=query_info,
            validation=None,
            statistical_analysis=None
        )

        return interpretation

    except Exception as e:
        # Fallback interpretation if generation fails
        return f"Analysis completed with {len(result.get('data', []))} results"
```

### Performance Considerations

**Current Performance** (from existing implementation):
- Simple queries: <5ms
- Grouped queries: <15ms
- Complex statistical interpretation: <30ms

**Target Performance** (new methods):
- `interpret_query_result()`: <10ms (thin wrapper, minimal overhead)
- `generate_analysis_suggestions()`: <25ms (delegation to existing methods)

**Optimization Notes**:
- New methods are thin adapters - minimal performance impact
- Existing implementation already optimized
- No additional database calls or heavy computation

### Testing Strategy

**Unit Tests** (to add):
```python
async def test_interpret_query_result_basic():
    engine = IntelligenceEngine()
    result = {"data": [{"plan": "pro", "users": 100}]}
    interpretation = await engine.interpret_query_result(
        result, dimensions=["plan"], measures=["users"]
    )
    assert isinstance(interpretation, str)
    assert len(interpretation) > 0

async def test_interpret_query_result_empty():
    engine = IntelligenceEngine()
    result = {"data": []}
    interpretation = await engine.interpret_query_result(result, [], [])
    assert interpretation == "No data returned for this query."

async def test_generate_analysis_suggestions():
    engine = IntelligenceEngine()
    result = {"data": [{"plan": "pro", "users": 100}]}
    suggestions = await engine.generate_analysis_suggestions(result)
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0
    assert "question" in suggestions[0]
    assert "reason" in suggestions[0]
```

---

## C - Completion Criteria

### Success Metrics

✅ **Method Signatures Match**:
- `interpret_query_result(result, dimensions, measures)` exists and is async
- `generate_analysis_suggestions(current_result, context)` exists and is async

✅ **Test Compatibility**:
- test_intelligence_engine() passes 100%
- test_integration() passes (uses interpret_query_result)

✅ **Backward Compatibility**:
- Existing methods still work (generate_interpretation, suggest_next_questions, etc.)
- No breaking changes to MCP tools using existing methods

✅ **Output Quality**:
- Interpretations are concise and natural (Mercury style)
- Suggestions are relevant and actionable
- Empty results handled gracefully

✅ **Performance**:
- `interpret_query_result()` executes in <10ms
- `generate_analysis_suggestions()` executes in <25ms
- No performance regression on existing methods

### Definition of Done

- [ ] Both methods implemented and tested
- [ ] All unit tests passing
- [ ] Integration test passing
- [ ] No regressions in existing functionality
- [ ] Code review completed
- [ ] Documentation updated

### Implementation Checklist

1. **Add `interpret_query_result()` method**:
   - [ ] Method signature matches spec
   - [ ] Delegates to `generate_interpretation()`
   - [ ] Handles edge cases (empty data, errors)
   - [ ] Returns concise string interpretation

2. **Add `generate_analysis_suggestions()` method**:
   - [ ] Method signature matches spec
   - [ ] Tries `suggest_next_questions()` first
   - [ ] Falls back to `suggest_analysis_paths()`
   - [ ] Returns list of {question, reason} dicts

3. **Testing**:
   - [ ] Add unit tests for both methods
   - [ ] Run test_all_functionality.py
   - [ ] Verify integration test passes

4. **Documentation**:
   - [ ] Add docstrings with examples
   - [ ] Update CLAUDE.md if needed

---

## Implementation Notes

### Recommended Approach

**Step 1**: Add `interpret_query_result()` as thin wrapper
```python
async def interpret_query_result(self, result, dimensions=[], measures=[]):
    query_info = {"dimensions": dimensions, "measures": measures}
    return await self.generate_interpretation(result, query_info)
```

**Step 2**: Add `generate_analysis_suggestions()` as delegator
```python
async def generate_analysis_suggestions(self, current_result=None, context=None):
    if current_result:
        dims = [k for k in current_result.get("data", [{}])[0].keys() if not any(m in k for m in ["total", "count", "rate"])]
        measures = [k for k in current_result.get("data", [{}])[0].keys() if k not in dims]
        return await self.suggest_next_questions(current_result, context or "", dims, measures)
    return await self.suggest_analysis_paths(current_result, context)
```

**Step 3**: Test and refine

### Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing MCP tools | HIGH | Keep all existing methods unchanged |
| Parameter extraction from result fails | MEDIUM | Add robust key detection logic |
| Performance degradation | LOW | Methods are thin wrappers, minimal overhead |

---

**Specification Version**: 1.0
**Created**: 2025-11-11
**Author**: Architect Agent
**Status**: Ready for Implementation
