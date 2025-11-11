# ConversationMemory - SPARC Specification

**Component**: `ConversationMemory` (mcp_server/conversation_memory.py)
**Status**: ❌ FAILING - API signature mismatch in `add_interaction()` method
**Priority**: MEDIUM - Blocks conversation tracking with model_used parameter

---

## S - Specification

### Problem Statement

The test calls `add_interaction()` with a different signature than what's implemented:

**Test expects**:
```python
interaction_id = memory.add_interaction(
    model_used="users",           # First positional arg
    dimensions=["plan_type"],
    measures=["total_users"],
    filters={},
    execution_time_ms=100,
    insights_generated=["Test insight"],
)
```

**Current implementation has**:
```python
def add_interaction(
    self,
    user_question: str,          # Different first arg!
    query_info: Dict[str, Any],
    result: Dict[str, Any],
    insights: List[str],
    statistical_analysis: Optional[Dict[str, Any]] = None,
) -> str:
```

### Required Fix

We need to support BOTH signatures:
1. **Keep existing signature** for MCP tools (backward compatibility)
2. **Add alternative overload** OR make existing method flexible

### Solution Approach

**Option A**: Make `add_interaction()` accept both signatures using flexible parameters
**Option B**: Add separate method `add_interaction_simple()` for test API
**Option C**: Make first parameter optional and detect signature based on parameters

**Recommended**: Option C (flexible parameter detection)

---

## API Contract (Flexible Signature)

```python
def add_interaction(
    self,
    model_used: Optional[str] = None,           # NEW: Can be first arg
    dimensions: Optional[List[str]] = None,     # NEW: Direct parameter
    measures: Optional[List[str]] = None,       # NEW: Direct parameter
    filters: Optional[Dict[str, Any]] = None,   # NEW: Direct parameter
    execution_time_ms: Optional[float] = None,  # NEW: Direct parameter
    insights_generated: Optional[List[str]] = None,  # NEW: Direct parameter
    user_question: Optional[str] = None,        # EXISTING: Keep for compatibility
    query_info: Optional[Dict[str, Any]] = None,  # EXISTING: Keep for compatibility
    result: Optional[Dict[str, Any]] = None,      # EXISTING: Keep for compatibility
    insights: Optional[List[str]] = None,         # EXISTING: Keep for compatibility
    statistical_analysis: Optional[Dict[str, Any]] = None,  # EXISTING: Keep
) -> str:
    """
    Add a new analysis interaction to memory.

    Supports two calling patterns:
    1. Simple (for tests): model_used, dimensions, measures, filters, execution_time_ms, insights_generated
    2. Complex (for MCP): user_question, query_info, result, insights, statistical_analysis

    Args:
        model_used: Semantic model name (simple pattern)
        dimensions: List of dimensions (simple pattern)
        measures: List of measures (simple pattern)
        filters: Filter dict (simple pattern)
        execution_time_ms: Query execution time (simple pattern)
        insights_generated: List of insights (simple pattern)
        user_question: Natural language question (complex pattern)
        query_info: Full query info dict (complex pattern)
        result: Query result dict (complex pattern)
        insights: Insights list (complex pattern)
        statistical_analysis: Statistical test results (complex pattern)

    Returns:
        Interaction ID (string)

    Examples:
        >>> # Simple pattern (tests)
        >>> memory.add_interaction(
        ...     model_used="users",
        ...     dimensions=["plan_type"],
        ...     measures=["total_users"],
        ...     filters={},
        ...     execution_time_ms=100,
        ...     insights_generated=["Pro plan has 2x users"]
        ... )
        'abc12345'

        >>> # Complex pattern (MCP tools)
        >>> memory.add_interaction(
        ...     user_question="How many users by plan?",
        ...     query_info={"model": "users", "dimensions": ["plan_type"], ...},
        ...     result={"data": [...], "execution_time_ms": 100},
        ...     insights=["Pro plan has 2x users"]
        ... )
        'def67890'
    """
    pass
```

---

## P - Pseudocode

### Algorithm (Pattern Detection)

```
FUNCTION add_interaction(**kwargs):
    # Detect which calling pattern is being used

    IF model_used IS PROVIDED:
        # Simple pattern (test API)
        RETURN _add_interaction_simple(
            model_used=model_used,
            dimensions=dimensions OR [],
            measures=measures OR [],
            filters=filters OR {},
            execution_time_ms=execution_time_ms OR 0,
            insights_generated=insights_generated OR []
        )

    ELSE IF user_question IS PROVIDED:
        # Complex pattern (MCP API)
        RETURN _add_interaction_complex(
            user_question=user_question,
            query_info=query_info OR {},
            result=result OR {},
            insights=insights OR [],
            statistical_analysis=statistical_analysis
        )

    ELSE:
        RAISE ValueError("Must provide either model_used or user_question")
    END IF
END FUNCTION

FUNCTION _add_interaction_simple(model_used, dimensions, measures, filters, execution_time_ms, insights_generated):
    # Build query_info from simple parameters
    query_info = {
        "model": model_used,
        "dimensions": dimensions,
        "measures": measures,
        "filters": filters
    }

    # Build result dict
    result = {
        "execution_time_ms": execution_time_ms,
        "data": [],  # No actual data in simple pattern
        "row_count": 0
    }

    # Call existing implementation with adapted parameters
    RETURN _add_interaction_internal(
        user_question="",  # Empty for simple pattern
        query_info=query_info,
        result=result,
        insights=insights_generated,
        statistical_analysis=None
    )
END FUNCTION

FUNCTION _add_interaction_complex(user_question, query_info, result, insights, statistical_analysis):
    # Call existing implementation directly
    RETURN _add_interaction_internal(
        user_question=user_question,
        query_info=query_info,
        result=result,
        insights=insights,
        statistical_analysis=statistical_analysis
    )
END FUNCTION

FUNCTION _add_interaction_internal(user_question, query_info, result, insights, statistical_analysis):
    # Existing implementation logic (lines 82-109 of current file)
    interaction_id = _generate_interaction_id(user_question, query_info)

    interaction = AnalysisInteraction(
        timestamp=NOW(),
        user_question=user_question,
        model_used=query_info.get("model", ""),
        dimensions=query_info.get("dimensions", []),
        measures=query_info.get("measures", []),
        filters=query_info.get("filters", {}),
        result_summary=_summarize_result(result),
        insights_generated=insights,
        statistical_tests=statistical_analysis,
        execution_time_ms=result.get("execution_time_ms", 0),
        interaction_id=interaction_id
    )

    self.interactions.append(interaction)
    _update_usage_patterns(interaction)
    _update_user_interests(interaction)
    _cleanup_old_interactions()

    RETURN interaction_id
END FUNCTION
```

**Complexity**: O(1) - Simple parameter transformation
**Performance**: <1ms overhead for pattern detection

---

## A - Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────┐
│        ConversationMemory (Public API)          │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌────────────────────────────────────────┐    │
│  │  Flexible add_interaction() Method     │    │
│  │                                         │    │
│  │  Parameters:                            │    │
│  │  • model_used (simple API)              │    │
│  │  • user_question (complex API)          │    │
│  │                                         │    │
│  │  Pattern Detection:                     │    │
│  │    IF model_used → Simple pattern       │    │
│  │    ELIF user_question → Complex pattern │    │
│  └──────────────┬──────────────────────────┘    │
│                 │                               │
│        ┌────────▼───────────┐                  │
│        │  Pattern Adapters  │                  │
│        │                    │                  │
│        │  Simple Pattern:   │                  │
│        │    Build query_info│                  │
│        │    from params     │                  │
│        │                    │                  │
│        │  Complex Pattern:  │                  │
│        │    Pass through    │                  │
│        └────────┬───────────┘                  │
│                 │                               │
│        ┌────────▼───────────────────────────┐  │
│        │  Existing Implementation           │  │
│        │                                     │  │
│        │  • Create AnalysisInteraction      │  │
│        │  • Update usage patterns           │  │
│        │  • Track user interests            │  │
│        │  • Return interaction_id           │  │
│        └────────────────────────────────────┘  │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Data Flow

```
Test API (Simple):
  memory.add_interaction(
    model_used="users",
    dimensions=["plan"],
    measures=["count"],
    ...
  )
    ↓
  Pattern Detection: model_used present
    ↓
  Build query_info dict from simple params
    ↓
  Call existing implementation
    ↓
  Return interaction_id

MCP API (Complex):
  memory.add_interaction(
    user_question="How many users?",
    query_info={...},
    result={...},
    insights=[...]
  )
    ↓
  Pattern Detection: user_question present
    ↓
  Pass through to existing implementation
    ↓
  Return interaction_id
```

---

## R - Refinement

### Edge Cases

1. **Both Patterns Provided** (conflict)
   ```python
   memory.add_interaction(
       model_used="users",  # Simple API
       user_question="test",  # Complex API - CONFLICT!
       ...
   )
   # Decision: Prefer simple API (model_used), ignore user_question
   ```

2. **Neither Pattern Provided**
   ```python
   memory.add_interaction()  # No parameters
   # Expected: ValueError("Must provide either model_used or user_question")
   ```

3. **Partial Parameters**
   ```python
   memory.add_interaction(model_used="users")
   # Expected: Use defaults for missing params (dimensions=[], measures=[], etc.)
   ```

4. **None Values**
   ```python
   memory.add_interaction(
       model_used="users",
       dimensions=None,  # Should default to []
       measures=None,    # Should default to []
       ...
   )
   ```

### Error Handling

```python
def add_interaction(
    self,
    model_used: Optional[str] = None,
    dimensions: Optional[List[str]] = None,
    measures: Optional[List[str]] = None,
    filters: Optional[Dict[str, Any]] = None,
    execution_time_ms: Optional[float] = None,
    insights_generated: Optional[List[str]] = None,
    user_question: Optional[str] = None,
    query_info: Optional[Dict[str, Any]] = None,
    result: Optional[Dict[str, Any]] = None,
    insights: Optional[List[str]] = None,
    statistical_analysis: Optional[Dict[str, Any]] = None,
) -> str:
    """Add interaction with flexible API."""

    # Pattern detection
    if model_used is not None:
        # Simple pattern (test API)
        query_info_built = {
            "model": model_used,
            "dimensions": dimensions or [],
            "measures": measures or [],
            "filters": filters or {},
        }

        result_built = {
            "execution_time_ms": execution_time_ms or 0,
            "data": [],
            "row_count": 0,
        }

        # Call existing implementation
        return self._add_interaction_internal(
            user_question="",
            query_info=query_info_built,
            result=result_built,
            insights=insights_generated or [],
            statistical_analysis=None,
        )

    elif user_question is not None or query_info is not None:
        # Complex pattern (MCP API)
        return self._add_interaction_internal(
            user_question=user_question or "",
            query_info=query_info or {},
            result=result or {},
            insights=insights or [],
            statistical_analysis=statistical_analysis,
        )

    else:
        raise ValueError("Must provide either model_used or user_question")
```

### Performance Considerations

**Current Performance**:
- `add_interaction()`: ~1-2ms (dict creation, list operations)

**Target Performance** (with flexible API):
- Simple pattern: ~2ms (1ms overhead for building dicts)
- Complex pattern: ~1ms (direct pass-through, no overhead)

**Optimization Notes**:
- Pattern detection is O(1) (simple if/elif checks)
- Dict building is O(n) where n = number of dimensions/measures (typically <10)
- No significant performance impact

---

## C - Completion Criteria

### Success Metrics

✅ **API Flexibility**:
- Method accepts both simple and complex calling patterns
- Tests pass with simple pattern
- MCP tools still work with complex pattern

✅ **Test Compatibility**:
- test_conversation_memory() passes 100%
- Test can call with model_used, dimensions, measures, etc.

✅ **Backward Compatibility**:
- Existing MCP tool calls still work
- No breaking changes to complex API

✅ **Error Handling**:
- Clear error when neither pattern provided
- Graceful handling of None values

✅ **Performance**:
- <2ms overhead for pattern adaptation

### Definition of Done

- [ ] Method updated to accept both patterns
- [ ] test_conversation_memory() passing
- [ ] No regressions in MCP tools
- [ ] Documentation updated with both patterns

### Implementation Checklist

1. **Refactor `add_interaction()` method**:
   - [ ] Add new optional parameters (model_used, dimensions, etc.)
   - [ ] Keep existing parameters (user_question, query_info, etc.)
   - [ ] Add pattern detection logic
   - [ ] Build query_info/result for simple pattern

2. **Extract existing logic**:
   - [ ] Optionally create `_add_interaction_internal()` helper
   - [ ] Move current implementation to helper
   - [ ] Call from both patterns

3. **Testing**:
   - [ ] Test simple pattern (model_used, dimensions, etc.)
   - [ ] Test complex pattern (user_question, query_info, etc.)
   - [ ] Test error cases (no parameters, conflicts)
   - [ ] Run test_all_functionality.py

4. **Documentation**:
   - [ ] Update docstring with both patterns
   - [ ] Add examples for each pattern

---

## Implementation Notes

### Recommended Approach

**Step 1**: Update method signature
```python
def add_interaction(
    self,
    # Simple API parameters (NEW)
    model_used: Optional[str] = None,
    dimensions: Optional[List[str]] = None,
    measures: Optional[List[str]] = None,
    filters: Optional[Dict[str, Any]] = None,
    execution_time_ms: Optional[float] = None,
    insights_generated: Optional[List[str]] = None,
    # Complex API parameters (EXISTING)
    user_question: Optional[str] = None,
    query_info: Optional[Dict[str, Any]] = None,
    result: Optional[Dict[str, Any]] = None,
    insights: Optional[List[str]] = None,
    statistical_analysis: Optional[Dict[str, Any]] = None,
) -> str:
```

**Step 2**: Add pattern detection
```python
    # Detect calling pattern
    if model_used is not None:
        # Simple pattern - build complex parameters
        query_info = {
            "model": model_used,
            "dimensions": dimensions or [],
            "measures": measures or [],
            "filters": filters or {},
        }
        result = {
            "execution_time_ms": execution_time_ms or 0,
            "data": [],
            "row_count": 0,
        }
        user_question = ""
        insights = insights_generated or []

    elif user_question is None and query_info is None:
        raise ValueError("Must provide either model_used or user_question")

    # Continue with existing implementation...
    interaction_id = self._generate_interaction_id(user_question or "", query_info or {})
    # ... rest of existing code ...
```

**Step 3**: Keep rest of implementation unchanged

### Testing the Method

```bash
cd semantic-layer
uv run python -c "
from mcp_server.conversation_memory import ConversationMemory

memory = ConversationMemory()

# Test simple pattern (for tests)
id1 = memory.add_interaction(
    model_used='users',
    dimensions=['plan_type'],
    measures=['total_users'],
    filters={},
    execution_time_ms=100,
    insights_generated=['Test insight']
)
print(f'Simple pattern: {id1}')

# Test complex pattern (for MCP)
id2 = memory.add_interaction(
    user_question='How many users?',
    query_info={'model': 'users', 'dimensions': ['plan'], 'measures': ['count']},
    result={'execution_time_ms': 50, 'data': []},
    insights=['Insight 2']
)
print(f'Complex pattern: {id2}')

print(f'Total interactions: {len(memory.interactions)}')
print('✅ Both patterns working!')
"
```

### Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking MCP tools | HIGH | Keep complex API parameters, add new ones |
| Parameter confusion | MEDIUM | Clear docstring with examples |
| Performance overhead | LOW | Minimal dict building, <1ms overhead |

---

**Specification Version**: 1.0
**Created**: 2025-11-11
**Author**: Architect Agent
**Status**: Ready for Implementation
