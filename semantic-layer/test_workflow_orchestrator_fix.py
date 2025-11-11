#!/usr/bin/env python3
"""
Test-Driven Development (TDD) Tests for WorkflowOrchestrator.list_available_templates()

RED Phase: Write tests first (they should fail)
GREEN Phase: Implement minimal solution to pass tests
REFACTOR Phase: Improve implementation
"""

from mcp_server.workflow_orchestrator import WorkflowOrchestrator, StepType


def test_list_available_templates_exists():
    """Test that list_available_templates method exists"""
    orchestrator = WorkflowOrchestrator()
    assert hasattr(orchestrator, "list_available_templates")
    assert callable(getattr(orchestrator, "list_available_templates"))
    print("✅ test_list_available_templates_exists PASSED")


def test_list_available_templates_returns_list():
    """Test that method returns a list"""
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.list_available_templates()
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    print("✅ test_list_available_templates_returns_list PASSED")


def test_list_available_templates_returns_all_three_templates():
    """Test that all 3 built-in templates are returned"""
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.list_available_templates()
    assert len(result) == 3, f"Expected 3 templates, got {len(result)}"

    # Check that all expected templates are present
    template_ids = [template["name"] for template in result]
    assert (
        "conversion_deep_dive" in template_ids
    ), "Missing conversion_deep_dive template"
    assert (
        "feature_usage_deep_dive" in template_ids
    ), "Missing feature_usage_deep_dive template"
    assert (
        "revenue_optimization" in template_ids
    ), "Missing revenue_optimization template"
    print("✅ test_list_available_templates_returns_all_three_templates PASSED")


def test_template_has_required_fields():
    """Test that each template has all required fields"""
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.list_available_templates()

    required_fields = [
        "name",
        "description",
        "steps",
        "step_types",
        "estimated_duration",
        "use_cases",
    ]

    for template in result:
        for field in required_fields:
            assert field in template, f"Template {template.get('name', 'unknown')} missing required field: {field}"
    print("✅ test_template_has_required_fields PASSED")


def test_template_name_field_is_string():
    """Test that name field is a string"""
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.list_available_templates()
    for template in result:
        assert isinstance(
            template["name"], str
        ), f"Template name should be string, got {type(template['name'])}"
        assert len(template["name"]) > 0, "Template name should not be empty"
    print("✅ test_template_name_field_is_string PASSED")


def test_template_description_field_is_string():
    """Test that description field is a string"""
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.list_available_templates()
    for template in result:
        assert isinstance(
            template["description"], str
        ), f"Template description should be string, got {type(template['description'])}"
        assert (
            len(template["description"]) > 0
        ), "Template description should not be empty"
    print("✅ test_template_description_field_is_string PASSED")


def test_template_steps_field_is_integer():
    """Test that steps field is an integer"""
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.list_available_templates()
    for template in result:
        assert isinstance(
            template["steps"], int
        ), f"Template steps should be integer, got {type(template['steps'])}"
        assert template["steps"] > 0, "Template should have at least 1 step"
    print("✅ test_template_steps_field_is_integer PASSED")


def test_template_step_types_is_list():
    """Test that step_types field is a list"""
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.list_available_templates()
    for template in result:
        assert isinstance(
            template["step_types"], list
        ), f"Template step_types should be list, got {type(template['step_types'])}"
        assert (
            len(template["step_types"]) > 0
        ), "Template should have at least 1 step type"
    print("✅ test_template_step_types_is_list PASSED")


def test_template_step_types_contains_valid_types():
    """Test that step_types contains valid StepType values"""
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.list_available_templates()

    valid_step_types = [
        "query",
        "analysis",
        "statistical_test",
        "insight_generation",
        "comparison",
        "aggregation",
    ]

    for template in result:
        for step_type in template["step_types"]:
            assert (
                step_type in valid_step_types
            ), f"Invalid step type: {step_type} in template {template['name']}"
    print("✅ test_template_step_types_contains_valid_types PASSED")


def test_template_estimated_duration_is_string():
    """Test that estimated_duration field is a string"""
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.list_available_templates()
    for template in result:
        assert isinstance(
            template["estimated_duration"], str
        ), f"Template estimated_duration should be string, got {type(template['estimated_duration'])}"
        assert (
            len(template["estimated_duration"]) > 0
        ), "Template estimated_duration should not be empty"
    print("✅ test_template_estimated_duration_is_string PASSED")


def test_template_use_cases_is_list():
    """Test that use_cases field is a list"""
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.list_available_templates()
    for template in result:
        assert isinstance(
            template["use_cases"], list
        ), f"Template use_cases should be list, got {type(template['use_cases'])}"
        assert (
            len(template["use_cases"]) > 0
        ), "Template should have at least 1 use case"
    print("✅ test_template_use_cases_is_list PASSED")


def test_template_use_cases_contains_strings():
    """Test that use_cases list contains strings"""
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.list_available_templates()
    for template in result:
        for use_case in template["use_cases"]:
            assert isinstance(
                use_case, str
            ), f"Use case should be string in template {template['name']}"
            assert len(use_case) > 0, "Use case should not be empty"
    print("✅ test_template_use_cases_contains_strings PASSED")


def test_conversion_deep_dive_template_metadata():
    """Test conversion_deep_dive template has correct metadata"""
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.list_available_templates()

    conversion_template = next(
        (t for t in result if t["name"] == "conversion_deep_dive"), None
    )
    assert conversion_template is not None, "conversion_deep_dive template not found"

    # Check specific metadata
    assert conversion_template["name"] == "conversion_deep_dive"
    assert "conversion" in conversion_template["description"].lower()
    assert conversion_template["steps"] == 5  # As defined in orchestrator

    # Check step types are present
    assert "query" in conversion_template["step_types"]
    assert "statistical_test" in conversion_template["step_types"]
    assert "insight_generation" in conversion_template["step_types"]
    print("✅ test_conversion_deep_dive_template_metadata PASSED")


def test_feature_usage_deep_dive_template_metadata():
    """Test feature_usage_deep_dive template has correct metadata"""
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.list_available_templates()

    feature_template = next(
        (t for t in result if t["name"] == "feature_usage_deep_dive"), None
    )
    assert feature_template is not None, "feature_usage_deep_dive template not found"

    # Check specific metadata
    assert feature_template["name"] == "feature_usage_deep_dive"
    assert "feature" in feature_template["description"].lower()
    assert feature_template["steps"] == 5  # As defined in orchestrator

    # Check step types are present
    assert "query" in feature_template["step_types"]
    assert "analysis" in feature_template["step_types"]
    assert "insight_generation" in feature_template["step_types"]
    print("✅ test_feature_usage_deep_dive_template_metadata PASSED")


def test_revenue_optimization_template_metadata():
    """Test revenue_optimization template has correct metadata"""
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.list_available_templates()

    revenue_template = next(
        (t for t in result if t["name"] == "revenue_optimization"), None
    )
    assert revenue_template is not None, "revenue_optimization template not found"

    # Check specific metadata
    assert revenue_template["name"] == "revenue_optimization"
    assert "revenue" in revenue_template["description"].lower()
    assert revenue_template["steps"] == 5  # As defined in orchestrator

    # Check step types are present
    assert "query" in revenue_template["step_types"]
    assert "analysis" in revenue_template["step_types"]
    assert "insight_generation" in revenue_template["step_types"]
    print("✅ test_revenue_optimization_template_metadata PASSED")


def test_template_step_count_matches_actual_steps():
    """Test that step count matches actual number of steps in template"""
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.list_available_templates()

    for template in result:
        template_id = template["name"]
        actual_template = orchestrator.workflow_templates[template_id]
        assert template["steps"] == len(
            actual_template.steps
        ), f"Step count mismatch for {template_id}: reported {template['steps']}, actual {len(actual_template.steps)}"
    print("✅ test_template_step_count_matches_actual_steps PASSED")


def test_template_step_types_match_actual_step_types():
    """Test that step_types list matches actual step types in template"""
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.list_available_templates()

    for template in result:
        template_id = template["name"]
        actual_template = orchestrator.workflow_templates[template_id]

        # Get actual unique step types from template
        actual_step_types = list(
            set(step.step_type.value for step in actual_template.steps)
        )

        # Check that reported step_types match actual step types
        for step_type in template["step_types"]:
            assert (
                step_type in actual_step_types
            ), f"Step type {step_type} not found in actual template {template_id}"
    print("✅ test_template_step_types_match_actual_step_types PASSED")


def test_no_duplicate_templates():
    """Test that there are no duplicate template names"""
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.list_available_templates()
    template_names = [t["name"] for t in result]

    # Check no duplicates
    assert len(template_names) == len(set(template_names)), "Duplicate template names found"
    print("✅ test_no_duplicate_templates PASSED")


def test_templates_are_complete_and_helpful():
    """Test that templates provide complete and helpful information"""
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.list_available_templates()

    for template in result:
        # Name should be meaningful
        assert len(template["name"]) > 5, f"Template name too short: {template['name']}"
        assert (
            "_" in template["name"] or "-" in template["name"]
        ), f"Template name should use underscores or hyphens: {template['name']}"

        # Description should be detailed (at least 20 characters)
        assert (
            len(template["description"]) > 20
        ), f"Template description too short: {template['description']}"

        # Should have at least 3 steps (complex workflow)
        assert (
            template["steps"] >= 3
        ), f"Template should have at least 3 steps: {template['name']}"

        # Should have at least 2 different step types
        assert len(template["step_types"]) >= 2, f"Template should have at least 2 step types: {template['name']}"

        # Estimated duration should mention time
        assert any(
            time_word in template["estimated_duration"].lower()
            for time_word in ["s", "sec", "min", "second", "minute", "-"]
        ), f"Estimated duration should mention time units: {template['estimated_duration']}"

        # Should have at least 2 use cases
        assert (
            len(template["use_cases"]) >= 2
        ), f"Template should have at least 2 use cases: {template['name']}"
    print("✅ test_templates_are_complete_and_helpful PASSED")


def test_return_value_is_json_serializable():
    """Test that return value can be serialized to JSON"""
    import json

    orchestrator = WorkflowOrchestrator()
    result = orchestrator.list_available_templates()

    # Should not raise exception
    json_string = json.dumps(result)
    assert isinstance(json_string, str)

    # Should be able to deserialize back
    deserialized = json.loads(json_string)
    assert deserialized == result
    print("✅ test_return_value_is_json_serializable PASSED")


def run_all_tests():
    """Run all tests and report results"""
    tests = [
        test_list_available_templates_exists,
        test_list_available_templates_returns_list,
        test_list_available_templates_returns_all_three_templates,
        test_template_has_required_fields,
        test_template_name_field_is_string,
        test_template_description_field_is_string,
        test_template_steps_field_is_integer,
        test_template_step_types_is_list,
        test_template_step_types_contains_valid_types,
        test_template_estimated_duration_is_string,
        test_template_use_cases_is_list,
        test_template_use_cases_contains_strings,
        test_conversion_deep_dive_template_metadata,
        test_feature_usage_deep_dive_template_metadata,
        test_revenue_optimization_template_metadata,
        test_template_step_count_matches_actual_steps,
        test_template_step_types_match_actual_step_types,
        test_no_duplicate_templates,
        test_templates_are_complete_and_helpful,
        test_return_value_is_json_serializable,
    ]

    print("\n" + "=" * 70)
    print("TDD RED PHASE: Running Tests (Expected to FAIL)")
    print("=" * 70 + "\n")

    passed = 0
    failed = 0
    errors = []

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            errors.append(f"❌ {test.__name__}: {str(e)}")
        except AttributeError as e:
            failed += 1
            errors.append(f"❌ {test.__name__}: Method not implemented - {str(e)}")
        except Exception as e:
            failed += 1
            errors.append(f"❌ {test.__name__}: Unexpected error - {str(e)}")

    print("\n" + "=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70 + "\n")

    if errors:
        print("Failed Tests:")
        for error in errors:
            print(f"  {error}")
        print()

    return passed, failed


if __name__ == "__main__":
    passed, failed = run_all_tests()

    if failed > 0:
        print("🔴 RED PHASE COMPLETE: Tests failing as expected")
        print("Next: Implement list_available_templates() method (GREEN PHASE)")
        exit(1)
    else:
        print("🟢 All tests passed!")
        exit(0)
