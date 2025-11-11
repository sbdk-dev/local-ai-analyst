# WorkflowOrchestrator - SPARC Specification

**Component**: `WorkflowOrchestrator` (mcp_server/workflow_orchestrator.py)
**Status**: ❌ FAILING - Missing `list_available_templates()` and `create_workflow_execution()` methods
**Priority**: HIGH - Blocks workflow discovery and template listing

---

## S - Specification

### Problem Statement

The test expects two methods that don't exist with the exact signatures:
1. `list_available_templates()` - Returns list of workflow template info
2. `create_workflow_execution(template_id)` - Creates workflow execution and returns ID

The implementation has:
- `list_available_workflows()` - Returns dict with templates key
- `create_workflow(template_id)` - Returns WorkflowExecution object

### Required API Contracts

#### Method 1: `list_available_templates()`

```python
def list_available_templates(self) -> List[Dict[str, Any]]:
    """
    List all available workflow templates.

    Returns:
        List of template dicts with keys: id, name, description, steps

    Examples:
        >>> orchestrator = WorkflowOrchestrator()
        >>> templates = orchestrator.list_available_templates()
        >>> templates[0]
        {
            "id": "conversion_deep_dive",
            "name": "Comprehensive Conversion Analysis",
            "description": "Multi-dimensional conversion rate analysis...",
            "steps": 5
        }
    """
    pass
```

**Type Signature**:
- **No parameters**
- **Returns**: `List[Dict[str, Any]]` - List of template info dicts
- **Synchronous** (not async)

**Required Behavior**:
1. MUST return list of dicts (not nested under "available_templates" key)
2. MUST include: id, name, description, steps (count)
3. MUST be synchronous
4. SHOULD return at least 3 templates (conversion, feature, revenue)

---

#### Method 2: `create_workflow_execution()`

```python
def create_workflow_execution(self, template_id: str) -> str:
    """
    Create a new workflow execution from template.

    Args:
        template_id: ID of the workflow template to instantiate

    Returns:
        Execution ID (string) for tracking the workflow

    Examples:
        >>> orchestrator = WorkflowOrchestrator()
        >>> execution_id = orchestrator.create_workflow_execution("conversion_deep_dive")
        >>> execution_id
        "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    """
    pass
```

**Type Signature**:
- `template_id: str` - Template identifier
- **Returns**: `str` - Execution ID (UUID string)
- **Synchronous** (not async) or **Async** (check test usage)

**Required Behavior**:
1. MUST create workflow execution from template
2. MUST return execution ID string (not WorkflowExecution object)
3. MUST store execution in self.active_workflows
4. MUST generate unique execution ID per call

---

### Integration Points

**Existing Methods to Preserve**:
- `create_workflow()` - Keep for complex workflow creation (async)
- `list_available_workflows()` - Keep for MCP tools (returns dict format)
- All execution methods unchanged

**New Methods Should**:
- Provide simplified API for tests
- Delegate to existing implementation
- Return simple types (list/str) instead of complex objects

---

## P - Pseudocode

### `list_available_templates()` Algorithm

```
FUNCTION list_available_templates():
    # Synchronous method - just reformats self.workflow_templates

    result = []

    FOR template_id, template_def IN self.workflow_templates.items():
        result.append({
            "id": template_id,
            "name": template_def.name,
            "description": template_def.description,
            "steps": LENGTH(template_def.steps)
        })
    END FOR

    RETURN result
END FUNCTION
```

**Complexity**: O(n) where n = number of templates (typically 3)
**Performance**: <1ms (simple dict iteration)

### `create_workflow_execution()` Algorithm

```
FUNCTION create_workflow_execution(template_id):
    # Check if template exists
    IF template_id NOT IN self.workflow_templates:
        RAISE ValueError("Unknown workflow template: {template_id}")
    END IF

    # Delegate to existing create_workflow method
    execution = AWAIT self.create_workflow(template_id, customizations=None)

    # Return just the execution ID (not the whole object)
    RETURN execution.execution_id
END FUNCTION
```

**Note**: If test calls this synchronously, we need to handle async internally:
```python
def create_workflow_execution(self, template_id):
    # Synchronous wrapper around async method
    execution_id = str(uuid.uuid4())

    # Directly create execution without async
    template = self.workflow_templates[template_id]
    execution = WorkflowExecution(
        workflow_id=template.workflow_id,
        execution_id=execution_id,
        definition=template
    )

    self.active_workflows[execution_id] = execution
    return execution_id
```

**Complexity**: O(1) - Simple object creation
**Performance**: <1ms

---

## A - Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────┐
│      WorkflowOrchestrator (Public API)          │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌────────────────────────────────────────┐    │
│  │  New Test-Compatible Methods           │    │
│  │                                         │    │
│  │  • list_available_templates() ───┐     │    │
│  │    (SYNC - simple list)          │     │    │
│  │                                   │     │    │
│  │  • create_workflow_execution() ──┼─┐   │    │
│  │    (Returns ID string)           │ │   │    │
│  └──────────────────────────────────┼─┼───┘    │
│                                     │ │         │
│                                     ▼ ▼         │
│  ┌────────────────────────────────────────┐    │
│  │  Internal State                        │    │
│  │                                         │    │
│  │  • self.workflow_templates (Dict)      │    │
│  │  • self.active_workflows (Dict)        │    │
│  │  • self.workflow_history (List)        │    │
│  └────────────────────────────────────────┘    │
│                                                 │
│  ┌────────────────────────────────────────┐    │
│  │  Existing Methods                      │    │
│  │                                         │    │
│  │  • create_workflow() (async, complex)  │    │
│  │  • list_available_workflows() (dict)   │    │
│  │  • execute_workflow() (async)          │    │
│  │  • get_workflow_status()               │    │
│  └────────────────────────────────────────┘    │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Data Flow

```
Template Discovery:
  Test → list_available_templates()
       → Formats self.workflow_templates
       → Returns List[Dict]

Workflow Creation:
  Test → create_workflow_execution("conversion_deep_dive")
       → Creates WorkflowExecution object
       → Stores in self.active_workflows
       → Returns execution_id (str)

Existing Flow (Keep):
  MCP Tool → create_workflow(template_id, customizations)
           → Returns full WorkflowExecution object
```

### Dependencies

**Required Imports** (already in file):
- `uuid` - For execution ID generation
- `typing.List, Dict, Any` - Type hints
- `WorkflowExecution` dataclass (already defined)

**Internal Dependencies**:
- `self.workflow_templates` (populated in __init__)
- `self.active_workflows` (dict tracking executions)

**External Dependencies**:
- None (methods use internal state only)

---

## R - Refinement

### Edge Cases

1. **No Templates Loaded**
   ```python
   orchestrator = WorkflowOrchestrator()
   # __init__ should load templates
   templates = orchestrator.list_available_templates()
   # Expected: [{"id": "conversion_deep_dive", ...}, ...]
   assert len(templates) >= 3
   ```

2. **Invalid Template ID**
   ```python
   orchestrator.create_workflow_execution("invalid_template_id")
   # Expected: ValueError("Unknown workflow template: invalid_template_id")
   ```

3. **Duplicate Execution IDs** (should never happen with UUID)
   ```python
   id1 = orchestrator.create_workflow_execution("conversion_deep_dive")
   id2 = orchestrator.create_workflow_execution("conversion_deep_dive")
   # Expected: id1 != id2 (different UUIDs)
   ```

### Error Handling

```python
def create_workflow_execution(self, template_id: str) -> str:
    """Create workflow execution from template."""
    # Validate template exists
    if template_id not in self.workflow_templates:
        raise ValueError(f"Unknown workflow template: {template_id}")

    try:
        # Generate unique execution ID
        execution_id = str(uuid.uuid4())

        # Get template definition
        template = self.workflow_templates[template_id]

        # Create execution (synchronous version)
        execution = WorkflowExecution(
            workflow_id=template.workflow_id,
            execution_id=execution_id,
            definition=template,
            status=WorkflowStatus.PENDING
        )

        # Store in active workflows
        self.active_workflows[execution_id] = execution

        return execution_id

    except Exception as e:
        raise RuntimeError(f"Failed to create workflow execution: {e}")
```

### Performance Considerations

**Current Performance**:
- `create_workflow()`: ~1-2ms (async with deep copy)
- `list_available_workflows()`: ~1ms (dict formatting)

**Target Performance** (new methods):
- `list_available_templates()`: <1ms (simple list formatting)
- `create_workflow_execution()`: <2ms (sync version of create)

**Optimization Notes**:
- New methods are thin wrappers or reformatters
- No async overhead if implemented synchronously
- Minimal object creation

### Testing Strategy

**Unit Tests** (to add):
```python
def test_list_available_templates():
    orchestrator = WorkflowOrchestrator()

    templates = orchestrator.list_available_templates()
    assert isinstance(templates, list)
    assert len(templates) >= 3

    # Check template structure
    template = templates[0]
    assert "id" in template
    assert "name" in template
    assert "description" in template
    assert "steps" in template
    assert isinstance(template["steps"], int)

def test_create_workflow_execution():
    orchestrator = WorkflowOrchestrator()

    execution_id = orchestrator.create_workflow_execution("conversion_deep_dive")
    assert isinstance(execution_id, str)
    assert len(execution_id) > 0

    # Verify execution was created
    status = orchestrator.get_workflow_status(execution_id)
    assert status is not None
    assert status["execution_id"] == execution_id

def test_create_workflow_execution_invalid():
    orchestrator = WorkflowOrchestrator()

    with pytest.raises(ValueError):
        orchestrator.create_workflow_execution("invalid_template")
```

---

## C - Completion Criteria

### Success Metrics

✅ **Method Signatures Match**:
- `list_available_templates()` exists and is synchronous
- `create_workflow_execution(template_id)` exists
- Returns match test expectations (list and string)

✅ **Test Compatibility**:
- test_workflow_orchestrator() passes 100%
- Returns expected 3+ templates
- Creates valid execution IDs

✅ **Backward Compatibility**:
- Existing `create_workflow()` still works
- Existing `list_available_workflows()` still works
- No breaking changes to MCP tools

✅ **Output Quality**:
- Templates include all required fields
- Execution IDs are unique UUIDs
- Executions properly tracked in active_workflows

✅ **Performance**:
- `list_available_templates()` < 1ms
- `create_workflow_execution()` < 2ms

### Definition of Done

- [ ] Both methods implemented
- [ ] test_workflow_orchestrator() passing
- [ ] No regressions in existing functionality
- [ ] Code review completed
- [ ] Documentation updated

### Implementation Checklist

1. **Add `list_available_templates()` method**:
   - [ ] Method is synchronous
   - [ ] Returns List[Dict] with id, name, description, steps
   - [ ] Returns all 3 built-in templates

2. **Add `create_workflow_execution()` method**:
   - [ ] Method validates template_id
   - [ ] Generates unique UUID execution_id
   - [ ] Creates and stores WorkflowExecution
   - [ ] Returns execution_id string

3. **Testing**:
   - [ ] Add unit tests
   - [ ] Run test_all_functionality.py
   - [ ] Verify test_workflow_orchestrator() passes

4. **Documentation**:
   - [ ] Add docstrings with examples
   - [ ] Update CLAUDE.md if needed

---

## Implementation Notes

### Recommended Approach

**Step 1**: Add `list_available_templates()`
```python
def list_available_templates(self) -> List[Dict[str, Any]]:
    """List all available workflow templates."""
    templates = []

    for template_id, template_def in self.workflow_templates.items():
        templates.append({
            "id": template_id,
            "name": template_def.name,
            "description": template_def.description,
            "steps": len(template_def.steps)
        })

    return templates
```

**Step 2**: Add `create_workflow_execution()`
```python
def create_workflow_execution(self, template_id: str) -> str:
    """Create workflow execution from template."""
    if template_id not in self.workflow_templates:
        raise ValueError(f"Unknown workflow template: {template_id}")

    # Generate unique execution ID
    execution_id = str(uuid.uuid4())

    # Get template
    template = self.workflow_templates[template_id]

    # Create execution
    execution = WorkflowExecution(
        workflow_id=template.workflow_id,
        execution_id=execution_id,
        definition=template,
        status=WorkflowStatus.PENDING
    )

    # Store
    self.active_workflows[execution_id] = execution

    return execution_id
```

**Placement**:
- `list_available_templates()` - Add after `_initialize_workflow_templates()`
- `create_workflow_execution()` - Add after `create_workflow()`

### Testing the Methods

```bash
cd semantic-layer
uv run python -c "
from mcp_server.workflow_orchestrator import WorkflowOrchestrator

# Test template listing
orchestrator = WorkflowOrchestrator()
templates = orchestrator.list_available_templates()
print(f'Templates: {len(templates)}')
for t in templates:
    print(f'  - {t[\"id\"]}: {t[\"name\"]} ({t[\"steps\"]} steps)')

# Test execution creation
execution_id = orchestrator.create_workflow_execution('conversion_deep_dive')
print(f'Created execution: {execution_id}')

# Test status retrieval
status = orchestrator.get_workflow_status(execution_id)
print(f'Status: {status[\"status\"]}')

print('✅ All methods working!')
"
```

### Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing create_workflow() | HIGH | Keep unchanged, add new method |
| UUID collision (extremely unlikely) | LOW | Use standard uuid.uuid4() |
| Test expects async | MEDIUM | Check test file, add async if needed |

---

## Additional Context

### Current Test Expectation (from test file)

```python
# Lines 103-112 of test_all_functionality.py
templates = orchestrator.list_available_templates()
assert len(templates) >= 3, f"Expected 3+ templates, got {len(templates)}"

execution_id = orchestrator.create_workflow_execution("conversion_deep_dive")
assert execution_id is not None, "Should create workflow execution"

status = orchestrator.get_workflow_status(execution_id)
assert status is not None, "Should return workflow status"
```

**Test requires**:
- `list_available_templates()` returns something with `len()` >= 3
- `create_workflow_execution()` returns non-None value
- Synchronous calls (no await shown in test)

### Relationship to Existing Methods

```python
# EXISTING (keep):
def list_available_workflows(self) -> Dict[str, Any]:
    """Returns dict with 'available_templates' key"""
    return {
        "available_templates": {...},
        "active_workflows": 5,
        "completed_workflows": 10
    }

# NEW (add):
def list_available_templates(self) -> List[Dict[str, Any]]:
    """Returns list of template dicts directly"""
    return [
        {"id": "...", "name": "...", "description": "...", "steps": 5},
        ...
    ]
```

---

**Specification Version**: 1.0
**Created**: 2025-11-11
**Author**: Architect Agent
**Status**: Ready for Implementation
