# StatisticalTester - SPARC Specification

**Component**: `StatisticalTester` (mcp_server/statistical_testing.py)
**Status**: ❌ FAILING - NoneType iteration error
**Priority**: MEDIUM - Blocks statistical testing functionality

---

## S - Specification

### Problem Statement

The test reports a NoneType iteration error:
```
argument of type 'NoneType' is not iterable
```

This suggests that somewhere in the code, we're trying to iterate over `None` when we expect a list, dict, or other iterable.

### Root Cause Analysis

Looking at the test (lines 149-173):
```python
async def test_statistical_tester():
    tester = StatisticalTester()

    mock_result = {
        "data": [
            {"plan_type": "free", "total_users": 100},
            {"plan_type": "pro", "total_users": 200},
        ]
    }

    validation = await tester.validate_result(mock_result, ["plan_type"])
    assert "sample_sizes" in validation

    significance = await tester.run_significance_tests(
        data=mock_result,
        comparison_type="groups",
        dimensions=["plan_type"],
        measures=["total_users"],
    )
    assert "tests" in significance
```

**Potential Issues**:

1. **In `validate_result()`**: May try to check `if dim in df.columns` where `dim` could be `None`
2. **In `run_significance_tests()`**: May expect return dict to have "tests" key but returns `None`
3. **In `auto_test_comparison()`**: Returns `None` in some edge cases but test expects dict

### Required Fixes

1. **Fix NoneType iteration in validation/testing methods**
2. **Ensure `validate_result()` always returns dict with required keys**
3. **Ensure `run_significance_tests()` always returns dict with "tests" key**
4. **Add null checks before checking membership (`in` operator)**

---

## API Contracts (No Changes Needed)

The existing API is correct, we just need to fix internal implementation bugs:

```python
async def validate_result(
    self, result: Dict[str, Any], dimensions: List[str]
) -> Dict[str, Any]:
    """
    Validate query results for statistical reliability.

    MUST return dict with keys: valid, warnings, sample_sizes, data_quality
    MUST handle None/empty dimensions gracefully
    MUST not raise exceptions on edge cases
    """
    pass

async def run_significance_tests(
    self,
    data: Dict[str, Any],
    comparison_type: str = "groups",
    dimensions: List[str] = [],
    measures: List[str] = [],
) -> Dict[str, Any]:
    """
    Run statistical significance tests on data.

    MUST return dict with "tests" key (even if empty)
    MUST handle None return from auto_test_comparison()
    MUST not iterate over None values
    """
    pass
```

---

## P - Pseudocode

### Fix 1: `validate_result()` - Null Check for Dimensions

**Current Issue** (line 63-64):
```python
dim = dimensions[0]  # Focus on primary dimension
if dim in df.columns:  # May fail if dim is None or dimensions is None
```

**Fix**:
```
FUNCTION validate_result(result, dimensions):
    validation = {
        "valid": True,
        "warnings": [],
        "sample_sizes": {},
        "data_quality": {}
    }

    data = result.get("data", [])
    IF data IS EMPTY:
        validation["valid"] = False
        validation["warnings"].append("No data returned")
        RETURN validation  # Early return with valid structure
    END IF

    df = DataFrame(data)

    # Check overall sample size
    total_rows = LENGTH(df)
    validation["sample_sizes"]["total"] = total_rows

    # Null check before accessing dimensions
    IF dimensions IS NOT None AND LENGTH(dimensions) > 0:
        dim = dimensions[0]

        # Null check before checking membership
        IF dim IS NOT None AND dim IN df.columns:
            group_sizes = df[dim].value_counts().to_dict()
            validation["sample_sizes"]["groups"] = group_sizes
            # ... rest of group validation ...
        END IF
    END IF

    # ... rest of validation ...

    RETURN validation
END FUNCTION
```

### Fix 2: `run_significance_tests()` - Handle None Return

**Current Issue** (line 303):
```python
return await self.auto_test_comparison(data, dimensions, measures)
```

If `auto_test_comparison` returns `None`, test fails because it expects dict with "tests" key.

**Fix**:
```
FUNCTION run_significance_tests(data, comparison_type, dimensions, measures):
    IF comparison_type == "groups":
        result = AWAIT auto_test_comparison(data, dimensions, measures)

        # Handle None return
        IF result IS None:
            RETURN {
                "tests": [],
                "message": "Insufficient data for statistical testing",
                "comparison_type": comparison_type
            }
        END IF

        # Wrap result in "tests" key if not already
        IF "tests" NOT IN result:
            RETURN {
                "tests": [result],
                "comparison_type": comparison_type
            }
        END IF

        RETURN result

    ELIF comparison_type == "correlation":
        result = AWAIT _correlation_test(data, dimensions, measures)
        RETURN {
            "tests": [result] IF result IS NOT None ELSE [],
            "comparison_type": "correlation"
        }

    ELIF comparison_type == "trend":
        result = AWAIT _trend_test(data, dimensions, measures)
        RETURN {
            "tests": [result] IF result IS NOT None ELSE [],
            "comparison_type": "trend"
        }

    ELSE:
        RETURN {
            "error": f"Unknown comparison type: {comparison_type}",
            "tests": []
        }
    END IF
END FUNCTION
```

### Fix 3: `auto_test_comparison()` - Better Null Handling

**Current Issue**: Returns `None` in many edge cases (lines 111-132)

**Fix**: Always return dict structure (can be empty/error, but not None)

```
FUNCTION auto_test_comparison(result, dimensions, measures):
    data = result.get("data", [])

    # Return error dict instead of None
    IF data IS EMPTY OR dimensions IS EMPTY OR measures IS EMPTY:
        RETURN {
            "test_type": "insufficient_data",
            "error": "Need data, dimensions, and measures for testing",
            "tests": []
        }
    END IF

    df = DataFrame(data)
    dim = dimensions[0]
    measure = measures[0]

    # Check columns exist (with null check)
    IF dim IS None OR dim NOT IN df.columns:
        RETURN {
            "test_type": "invalid_dimension",
            "error": f"Dimension '{dim}' not found in data",
            "tests": []
        }
    END IF

    IF measure IS None OR measure NOT IN df.columns:
        RETURN {
            "test_type": "invalid_measure",
            "error": f"Measure '{measure}' not found in data",
            "tests": []
        }
    END IF

    # ... rest of testing logic ...

    # Ensure we always return dict (never None)
    IF test_result IS None:
        RETURN {
            "test_type": "no_test_performed",
            "tests": []
        }
    END IF

    RETURN test_result
END FUNCTION
```

---

## A - Architecture

### Error Propagation Flow

```
┌─────────────────────────────────────┐
│  run_significance_tests()           │
│  (Entry point from test)            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  auto_test_comparison()             │
│  • Add null checks                  │
│  • Return dict (never None)         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  _two_group_test() /                │
│  _multiple_group_test()             │
│  • Already return dicts             │
└─────────────────────────────────────┘
```

### Defensive Programming Pattern

```python
# Pattern: Always return valid dict structure

def some_method() -> Dict[str, Any]:
    # Start with valid structure
    result = {
        "success": False,
        "data": [],
        "error": None
    }

    try:
        # Do work...
        if some_condition:
            result["success"] = True
            result["data"] = [...]
        else:
            result["error"] = "Some issue"

    except Exception as e:
        result["error"] = str(e)

    # Always return dict (never None)
    return result
```

---

## R - Refinement

### Edge Cases to Fix

1. **Empty Data**
   ```python
   result = {"data": []}
   validation = await tester.validate_result(result, ["plan_type"])
   # Must return: {"valid": False, "warnings": ["No data returned"], ...}
   ```

2. **None Dimensions**
   ```python
   result = {"data": [...]}
   validation = await tester.validate_result(result, None)
   # Must handle: Check if dimensions is None before accessing
   ```

3. **Empty Dimensions List**
   ```python
   validation = await tester.validate_result(result, [])
   # Must handle: Don't try to access dimensions[0]
   ```

4. **Dimension Not in DataFrame**
   ```python
   result = {"data": [{"col1": 1}]}
   validation = await tester.validate_result(result, ["nonexistent"])
   # Must handle: Don't crash, add warning
   ```

5. **None Return from auto_test_comparison**
   ```python
   significance = await tester.run_significance_tests(...)
   # Must return: {"tests": [], "message": "..."}
   ```

### Error Handling Fixes

#### Fix 1: validate_result() - Line 63-64

**Before**:
```python
dim = dimensions[0]  # Crashes if dimensions is None or empty
if dim in df.columns:
```

**After**:
```python
if dimensions and len(dimensions) > 0:
    dim = dimensions[0]
    if dim and dim in df.columns:
        # Safe to proceed
```

#### Fix 2: auto_test_comparison() - Line 120-122

**Before**:
```python
if dim not in df.columns or measure not in df.columns:
    return None  # Causes test to fail
```

**After**:
```python
if not dim or dim not in df.columns:
    return {
        "test_type": "invalid_dimension",
        "error": f"Dimension not found: {dim}",
        "tests": []
    }
if not measure or measure not in df.columns:
    return {
        "test_type": "invalid_measure",
        "error": f"Measure not found: {measure}",
        "tests": []
    }
```

#### Fix 3: run_significance_tests() - Line 303

**Before**:
```python
return await self.auto_test_comparison(data, dimensions, measures)
# Returns None sometimes, test expects dict with "tests" key
```

**After**:
```python
result = await self.auto_test_comparison(data, dimensions, measures)
if result is None or "error" in result:
    return {
        "tests": [],
        "comparison_type": comparison_type,
        "message": result.get("error") if result else "No test performed"
    }

# Wrap in expected format
if "tests" not in result:
    return {
        "tests": [result],
        "comparison_type": comparison_type
    }

return result
```

---

## C - Completion Criteria

### Success Metrics

✅ **No NoneType Errors**:
- All `in` checks preceded by null checks
- All list/dict accesses checked for None
- No crashes on edge cases

✅ **Test Compatibility**:
- test_statistical_tester() passes 100%
- validate_result() returns dict with required keys
- run_significance_tests() returns dict with "tests" key

✅ **Graceful Degradation**:
- Empty data returns valid error dict
- None dimensions handled gracefully
- Invalid dimensions/measures return error dict (not None)

✅ **Backward Compatibility**:
- No breaking changes to existing valid use cases
- Statistical tests still work correctly with valid data

### Definition of Done

- [ ] All None checks added
- [ ] validate_result() never crashes
- [ ] run_significance_tests() always returns dict with "tests"
- [ ] auto_test_comparison() never returns None
- [ ] test_statistical_tester() passing
- [ ] No regressions in valid test cases

### Implementation Checklist

1. **Fix `validate_result()` (lines 27-101)**:
   - [ ] Add null check before `dimensions[0]`
   - [ ] Add null check before `dim in df.columns`
   - [ ] Ensure always returns valid dict structure

2. **Fix `auto_test_comparison()` (lines 103-164)**:
   - [ ] Replace `return None` with error dicts
   - [ ] Add null checks before column checks
   - [ ] Ensure always returns dict with "test_type"

3. **Fix `run_significance_tests()` (lines 282-310)**:
   - [ ] Handle None return from auto_test_comparison
   - [ ] Wrap results in "tests" key
   - [ ] Return error dict for unknown comparison types

4. **Testing**:
   - [ ] Test with empty data
   - [ ] Test with None dimensions
   - [ ] Test with invalid dimensions
   - [ ] Run test_all_functionality.py

---

## Implementation Notes

### Quick Fixes (Priority Order)

**Fix 1**: Line 63 - validate_result()
```python
# Before
dim = dimensions[0]
if dim in df.columns:

# After
if dimensions and len(dimensions) > 0:
    dim = dimensions[0]
    if dim and dim in df.columns:
```

**Fix 2**: Lines 120-122 - auto_test_comparison()
```python
# Before
if dim not in df.columns or measure not in df.columns:
    return None

# After
if not dim or dim not in df.columns:
    return {"test_type": "error", "error": "Invalid dimension", "tests": []}
if not measure or measure not in df.columns:
    return {"test_type": "error", "error": "Invalid measure", "tests": []}
```

**Fix 3**: Line 303 - run_significance_tests()
```python
# Before
if comparison_type == "groups":
    return await self.auto_test_comparison(data, dimensions, measures)

# After
if comparison_type == "groups":
    result = await self.auto_test_comparison(data, dimensions, measures)
    if not result or "error" in result:
        return {"tests": [], "message": result.get("error") if result else "No test"}
    return {"tests": [result]} if "tests" not in result else result
```

### Testing the Fixes

```bash
cd semantic-layer
uv run python -c "
import asyncio
from mcp_server.statistical_testing import StatisticalTester

async def test():
    tester = StatisticalTester()

    # Test with valid data
    mock_result = {
        'data': [
            {'plan_type': 'free', 'total_users': 100},
            {'plan_type': 'pro', 'total_users': 200},
        ]
    }

    validation = await tester.validate_result(mock_result, ['plan_type'])
    print(f'Validation: {list(validation.keys())}')
    assert 'sample_sizes' in validation

    significance = await tester.run_significance_tests(
        data=mock_result,
        comparison_type='groups',
        dimensions=['plan_type'],
        measures=['total_users'],
    )
    print(f'Significance: {list(significance.keys())}')
    assert 'tests' in significance

    # Test edge cases
    validation2 = await tester.validate_result({'data': []}, ['plan'])
    print(f'Empty data validation: {validation2}')

    print('✅ All tests passing!')

asyncio.run(test())
"
```

### Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking valid statistical tests | HIGH | Only add defensive checks, don't change logic |
| Over-defensive error handling | LOW | Return informative error messages |
| Test still fails after fixes | MEDIUM | Debug with print statements to find exact issue |

---

## Additional Debugging

If test still fails after fixes, add debug logging:

```python
async def validate_result(self, result, dimensions):
    print(f"DEBUG: result keys: {result.keys() if result else 'None'}")
    print(f"DEBUG: dimensions: {dimensions}")
    print(f"DEBUG: dimensions type: {type(dimensions)}")

    validation = {...}

    # ... rest of method ...
```

Run test and check output for exact failure point.

---

**Specification Version**: 1.0
**Created**: 2025-11-11
**Author**: Architect Agent
**Status**: Ready for Implementation
