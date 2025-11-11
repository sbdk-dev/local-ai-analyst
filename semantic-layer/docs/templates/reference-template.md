# [Feature/API Name] Reference

**Category**: [API / Configuration / Tool / etc.]
**Version**: [Version when introduced]
**Status**: Stable | Beta | Experimental

---

## Overview

[1-2 sentence description of what this reference documents]

---

## Quick Reference

### Basic Usage

```python
# Minimal working example
basic_usage_example()
```

### Common Patterns

```python
# Most common use case
common_pattern_example()
```

---

## Complete Specification

### [Function/Tool/Feature Name 1]

**Description**: [What it does]

**Signature**:
```python
def function_name(
    param1: str,
    param2: int = 10,
    param3: Optional[dict] = None
) -> ReturnType:
    """Detailed docstring"""
```

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `param1` | `str` | Yes | - | [Parameter description] |
| `param2` | `int` | No | `10` | [Parameter description] |
| `param3` | `dict` | No | `None` | [Parameter description] |

**Returns**:
- **Type**: `ReturnType`
- **Description**: [What the return value represents]

**Example**:
```python
# Example usage with explanation
result = function_name(
    param1="value",
    param2=20
)

# Expected output
print(result)
# Output: expected_output_here
```

**Errors**:

| Error | Condition | Resolution |
|-------|-----------|------------|
| `ValueError` | [When it occurs] | [How to fix] |
| `TypeError` | [When it occurs] | [How to fix] |

---

### [Function/Tool/Feature Name 2]

[Continue pattern for each item in the reference]

---

## Advanced Usage

### [Advanced Pattern 1]

[Description of advanced usage pattern]

```python
# Advanced example
advanced_example()
```

**When to Use**: [Scenarios where this pattern is appropriate]

### [Advanced Pattern 2]

[Continue pattern]

---

## Configuration Options

### [Config Category 1]

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `option_1` | `str` | `"default"` | [What it controls] |
| `option_2` | `bool` | `true` | [What it controls] |

**Example Configuration**:
```yaml
config:
  option_1: "custom_value"
  option_2: false
```

---

## Performance Characteristics

### Time Complexity
- [Description of performance: O(n), O(1), etc.]

### Memory Usage
- [Typical memory footprint]

### Caching Behavior
- [If applicable: caching strategy]

---

## Examples by Use Case

### Use Case 1: [Description]

```python
# Complete working example for this use case
example_code()
```

### Use Case 2: [Description]

[Continue pattern]

---

## See Also

- **Related Reference**: [Link to related API/feature]
- **Concept Guide**: [Link to conceptual explanation]
- **Tutorial**: [Link to tutorial using this feature]

---

## Changelog

### Version X.X
- Added: [New features]
- Changed: [Breaking changes]
- Deprecated: [Deprecated features]

---

**Last Updated**: YYYY-MM-DD
**API Version**: X.X.X
**Feedback**: [Issue link]
