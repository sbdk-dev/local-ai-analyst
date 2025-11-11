#!/usr/bin/env python3
"""
Test-Driven Development (TDD) Tests for WorkflowOrchestrator.list_available_templates()

RED Phase: Write tests first (they should fail)
GREEN Phase: Implement minimal solution to pass tests
REFACTOR Phase: Improve implementation
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.workflow_orchestrator import WorkflowOrchestrator, StepType


class TestListAvailableTemplates:
    """Test suite for list_available_templates() method"""

    def setup_method(self):
        """Setup test fixtures"""
        self.orchestrator = WorkflowOrchestrator()

    def test_list_available_templates_exists(self):
        """Test that list_available_templates method exists"""
        assert hasattr(self.orchestrator, "list_available_templates")
        assert callable(getattr(self.orchestrator, "list_available_templates"))

    def test_list_available_templates_returns_list(self):
        """Test that method returns a list"""
        result = self.orchestrator.list_available_templates()
        assert isinstance(result, list)

    def test_list_available_templates_returns_all_three_templates(self):
        """Test that all 3 built-in templates are returned"""
        result = self.orchestrator.list_available_templates()
        assert len(result) == 3

        # Check that all expected templates are present
        template_ids = [template["name"] for template in result]
        assert "conversion_deep_dive" in template_ids
        assert "feature_usage_deep_dive" in template_ids
        assert "revenue_optimization" in template_ids

    def test_template_has_required_fields(self):
        """Test that each template has all required fields"""
        result = self.orchestrator.list_available_templates()

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
                assert field in template, f"Template missing required field: {field}"

    def test_template_name_field_is_string(self):
        """Test that name field is a string"""
        result = self.orchestrator.list_available_templates()
        for template in result:
            assert isinstance(template["name"], str)
            assert len(template["name"]) > 0

    def test_template_description_field_is_string(self):
        """Test that description field is a string"""
        result = self.orchestrator.list_available_templates()
        for template in result:
            assert isinstance(template["description"], str)
            assert len(template["description"]) > 0

    def test_template_steps_field_is_integer(self):
        """Test that steps field is an integer"""
        result = self.orchestrator.list_available_templates()
        for template in result:
            assert isinstance(template["steps"], int)
            assert template["steps"] > 0

    def test_template_step_types_is_list(self):
        """Test that step_types field is a list"""
        result = self.orchestrator.list_available_templates()
        for template in result:
            assert isinstance(template["step_types"], list)
            assert len(template["step_types"]) > 0

    def test_template_step_types_contains_valid_types(self):
        """Test that step_types contains valid StepType values"""
        result = self.orchestrator.list_available_templates()

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
                ), f"Invalid step type: {step_type}"

    def test_template_estimated_duration_is_string(self):
        """Test that estimated_duration field is a string"""
        result = self.orchestrator.list_available_templates()
        for template in result:
            assert isinstance(template["estimated_duration"], str)
            assert len(template["estimated_duration"]) > 0

    def test_template_use_cases_is_list(self):
        """Test that use_cases field is a list"""
        result = self.orchestrator.list_available_templates()
        for template in result:
            assert isinstance(template["use_cases"], list)
            assert len(template["use_cases"]) > 0

    def test_template_use_cases_contains_strings(self):
        """Test that use_cases list contains strings"""
        result = self.orchestrator.list_available_templates()
        for template in result:
            for use_case in template["use_cases"]:
                assert isinstance(use_case, str)
                assert len(use_case) > 0

    def test_conversion_deep_dive_template_metadata(self):
        """Test conversion_deep_dive template has correct metadata"""
        result = self.orchestrator.list_available_templates()

        conversion_template = next(
            t for t in result if t["name"] == "conversion_deep_dive"
        )

        # Check specific metadata
        assert conversion_template["name"] == "conversion_deep_dive"
        assert "conversion" in conversion_template["description"].lower()
        assert conversion_template["steps"] == 5  # As defined in orchestrator

        # Check step types are present
        assert "query" in conversion_template["step_types"]
        assert "statistical_test" in conversion_template["step_types"]
        assert "insight_generation" in conversion_template["step_types"]

    def test_feature_usage_deep_dive_template_metadata(self):
        """Test feature_usage_deep_dive template has correct metadata"""
        result = self.orchestrator.list_available_templates()

        feature_template = next(
            t for t in result if t["name"] == "feature_usage_deep_dive"
        )

        # Check specific metadata
        assert feature_template["name"] == "feature_usage_deep_dive"
        assert "feature" in feature_template["description"].lower()
        assert feature_template["steps"] == 5  # As defined in orchestrator

        # Check step types are present
        assert "query" in feature_template["step_types"]
        assert "analysis" in feature_template["step_types"]
        assert "insight_generation" in feature_template["step_types"]

    def test_revenue_optimization_template_metadata(self):
        """Test revenue_optimization template has correct metadata"""
        result = self.orchestrator.list_available_templates()

        revenue_template = next(
            t for t in result if t["name"] == "revenue_optimization"
        )

        # Check specific metadata
        assert revenue_template["name"] == "revenue_optimization"
        assert "revenue" in revenue_template["description"].lower()
        assert revenue_template["steps"] == 5  # As defined in orchestrator

        # Check step types are present
        assert "query" in revenue_template["step_types"]
        assert "analysis" in revenue_template["step_types"]
        assert "insight_generation" in revenue_template["step_types"]

    def test_template_step_count_matches_actual_steps(self):
        """Test that step count matches actual number of steps in template"""
        result = self.orchestrator.list_available_templates()

        for template in result:
            template_id = template["name"]
            actual_template = self.orchestrator.workflow_templates[template_id]
            assert template["steps"] == len(actual_template.steps)

    def test_template_step_types_match_actual_step_types(self):
        """Test that step_types list matches actual step types in template"""
        result = self.orchestrator.list_available_templates()

        for template in result:
            template_id = template["name"]
            actual_template = self.orchestrator.workflow_templates[template_id]

            # Get actual unique step types from template
            actual_step_types = list(
                set(step.step_type.value for step in actual_template.steps)
            )

            # Check that reported step_types match actual step types
            for step_type in template["step_types"]:
                assert (
                    step_type in actual_step_types
                ), f"Step type {step_type} not found in actual template {template_id}"

    def test_no_duplicate_templates(self):
        """Test that there are no duplicate template names"""
        result = self.orchestrator.list_available_templates()
        template_names = [t["name"] for t in result]

        # Check no duplicates
        assert len(template_names) == len(set(template_names))

    def test_templates_are_complete_and_helpful(self):
        """Test that templates provide complete and helpful information"""
        result = self.orchestrator.list_available_templates()

        for template in result:
            # Name should be meaningful
            assert len(template["name"]) > 5
            assert "_" in template["name"] or "-" in template["name"]

            # Description should be detailed (at least 20 characters)
            assert len(template["description"]) > 20

            # Should have at least 3 steps (complex workflow)
            assert template["steps"] >= 3

            # Should have at least 2 different step types
            assert len(template["step_types"]) >= 2

            # Estimated duration should mention time
            assert any(
                time_word in template["estimated_duration"].lower()
                for time_word in ["s", "sec", "min", "second", "minute", "-"]
            )

            # Should have at least 2 use cases
            assert len(template["use_cases"]) >= 2

    def test_return_value_is_json_serializable(self):
        """Test that return value can be serialized to JSON"""
        import json

        result = self.orchestrator.list_available_templates()

        # Should not raise exception
        json_string = json.dumps(result)
        assert isinstance(json_string, str)

        # Should be able to deserialize back
        deserialized = json.loads(json_string)
        assert deserialized == result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
