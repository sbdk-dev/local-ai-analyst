#!/usr/bin/env python3
"""
Integration test for list_available_templates() with MCP server
"""

import asyncio
from mcp_server.workflow_orchestrator import WorkflowOrchestrator


async def test_integration():
    """Test that list_available_templates integrates properly"""
    print("=" * 70)
    print("Integration Test: list_available_templates()")
    print("=" * 70 + "\n")

    orchestrator = WorkflowOrchestrator()

    # Test 1: List templates
    print("✓ Test 1: Listing available templates...")
    templates = orchestrator.list_available_templates()
    assert len(templates) == 3
    print(f"  Found {len(templates)} templates")

    # Test 2: Verify each template can be used to create a workflow
    print("\n✓ Test 2: Creating workflows from templates...")
    for template in templates:
        template_id = template["name"]
        print(f"  Creating workflow from: {template_id}")

        execution = await orchestrator.create_workflow(template_id)
        assert execution is not None
        assert execution.workflow_id == template_id
        assert len(execution.definition.steps) == template["steps"]

        print(
            f"    ✓ Created execution {execution.execution_id[:8]}... with {len(execution.definition.steps)} steps"
        )

    # Test 3: Verify template metadata matches actual template structure
    print("\n✓ Test 3: Verifying template metadata accuracy...")
    for template in templates:
        template_id = template["name"]
        actual_template = orchestrator.workflow_templates[template_id]

        # Verify step count
        assert template["steps"] == len(actual_template.steps), f"Step count mismatch for {template_id}"

        # Verify step types
        actual_step_types = set(step.step_type.value for step in actual_template.steps)
        reported_step_types = set(template["step_types"])
        assert reported_step_types == actual_step_types, f"Step types mismatch for {template_id}"

        print(f"  ✓ {template_id}: metadata accurate")

    # Test 4: Verify template customization still works
    print("\n✓ Test 4: Testing template customization...")
    customizations = {
        "steps": {
            "baseline_conversion": {
                "parameters": {
                    "limit": 100,
                }
            }
        }
    }

    execution = await orchestrator.create_workflow("conversion_deep_dive", customizations)
    baseline_step = next(
        (s for s in execution.definition.steps if s.step_id == "baseline_conversion"),
        None,
    )
    assert baseline_step is not None
    assert baseline_step.parameters.get("limit") == 100
    print("  ✓ Template customization working")

    # Test 5: Verify JSON serialization
    print("\n✓ Test 5: Testing JSON serialization...")
    import json

    json_output = json.dumps(templates, indent=2)
    deserialized = json.loads(json_output)
    assert deserialized == templates
    print("  ✓ Templates are JSON serializable")

    print("\n" + "=" * 70)
    print("✅ All Integration Tests Passed!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_integration())
