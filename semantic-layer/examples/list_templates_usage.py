#!/usr/bin/env python3
"""
Usage Examples for list_available_templates()

This demonstrates how to use the new list_available_templates() method
to discover and work with workflow templates.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.workflow_orchestrator import WorkflowOrchestrator


def example_1_list_all_templates():
    """Example 1: List all available templates"""
    print("\n" + "=" * 70)
    print("Example 1: List All Available Templates")
    print("=" * 70 + "\n")

    orchestrator = WorkflowOrchestrator()
    templates = orchestrator.list_available_templates()

    print(f"Found {len(templates)} workflow templates:\n")

    for i, template in enumerate(templates, 1):
        print(f"{i}. {template['name']}")
        print(f"   Description: {template['description']}")
        print(f"   Steps: {template['steps']}")
        print(f"   Duration: {template['estimated_duration']}")
        print(f"   Step Types: {', '.join(template['step_types'])}")
        print()


def example_2_filter_by_use_case():
    """Example 2: Filter templates by use case"""
    print("\n" + "=" * 70)
    print("Example 2: Filter Templates by Use Case")
    print("=" * 70 + "\n")

    orchestrator = WorkflowOrchestrator()
    templates = orchestrator.list_available_templates()

    search_term = "conversion"
    print(f"Searching for templates with '{search_term}' in use cases:\n")

    matching = []
    for template in templates:
        for use_case in template["use_cases"]:
            if search_term.lower() in use_case.lower():
                matching.append(template)
                break

    for template in matching:
        print(f"✓ {template['name']}")
        print(f"  Relevant use cases:")
        for use_case in template["use_cases"]:
            if search_term.lower() in use_case.lower():
                print(f"    - {use_case}")
        print()


def example_3_find_by_step_type():
    """Example 3: Find templates by step type"""
    print("\n" + "=" * 70)
    print("Example 3: Find Templates by Step Type")
    print("=" * 70 + "\n")

    orchestrator = WorkflowOrchestrator()
    templates = orchestrator.list_available_templates()

    step_type = "statistical_test"
    print(f"Finding templates that include '{step_type}' step type:\n")

    for template in templates:
        if step_type in template["step_types"]:
            print(f"✓ {template['name']}")
            print(f"  All step types: {', '.join(template['step_types'])}")
            print()


def example_4_compare_templates():
    """Example 4: Compare template complexity"""
    print("\n" + "=" * 70)
    print("Example 4: Compare Template Complexity")
    print("=" * 70 + "\n")

    orchestrator = WorkflowOrchestrator()
    templates = orchestrator.list_available_templates()

    print("Template Complexity Comparison:\n")
    print(f"{'Template':<30} {'Steps':<8} {'Step Types':<15} {'Duration'}")
    print("-" * 70)

    for template in templates:
        print(
            f"{template['name']:<30} "
            f"{template['steps']:<8} "
            f"{len(template['step_types']):<15} "
            f"{template['estimated_duration']}"
        )


def example_5_json_export():
    """Example 5: Export templates to JSON"""
    print("\n" + "=" * 70)
    print("Example 5: Export Templates to JSON")
    print("=" * 70 + "\n")

    orchestrator = WorkflowOrchestrator()
    templates = orchestrator.list_available_templates()

    # Export to JSON
    json_output = json.dumps(templates, indent=2)

    print("Templates exported to JSON format:")
    print(json_output[:500] + "...")  # Show first 500 chars
    print(f"\nTotal JSON size: {len(json_output)} characters")


def example_6_template_recommendations():
    """Example 6: Recommend template based on analysis goal"""
    print("\n" + "=" * 70)
    print("Example 6: Template Recommendations")
    print("=" * 70 + "\n")

    orchestrator = WorkflowOrchestrator()
    templates = orchestrator.list_available_templates()

    # Define analysis goals
    analysis_goals = {
        "revenue": "revenue_optimization",
        "feature": "feature_usage_deep_dive",
        "conversion": "conversion_deep_dive",
        "user behavior": "feature_usage_deep_dive",
        "pricing": "revenue_optimization",
    }

    print("Template Recommendations by Analysis Goal:\n")

    for goal, recommended_template_id in analysis_goals.items():
        template = next((t for t in templates if t["name"] == recommended_template_id), None)
        if template:
            print(f"Goal: {goal.upper()}")
            print(f"  → Recommended: {template['name']}")
            print(f"  → Why: {template['description']}")
            print(f"  → Duration: {template['estimated_duration']}")
            print()


def example_7_detailed_template_info():
    """Example 7: Get detailed info for specific template"""
    print("\n" + "=" * 70)
    print("Example 7: Detailed Template Information")
    print("=" * 70 + "\n")

    orchestrator = WorkflowOrchestrator()
    templates = orchestrator.list_available_templates()

    # Get detailed info for conversion_deep_dive
    template_name = "conversion_deep_dive"
    template = next((t for t in templates if t["name"] == template_name), None)

    if template:
        print(f"Template: {template['name']}\n")
        print(f"Description: {template['description']}\n")
        print(f"Workflow Details:")
        print(f"  • Total Steps: {template['steps']}")
        print(f"  • Step Types: {', '.join(template['step_types'])}")
        print(f"  • Estimated Duration: {template['estimated_duration']}\n")
        print(f"Use Cases:")
        for i, use_case in enumerate(template["use_cases"], 1):
            print(f"  {i}. {use_case}")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("WorkflowOrchestrator.list_available_templates() Usage Examples")
    print("=" * 70)

    example_1_list_all_templates()
    example_2_filter_by_use_case()
    example_3_find_by_step_type()
    example_4_compare_templates()
    example_5_json_export()
    example_6_template_recommendations()
    example_7_detailed_template_info()

    print("\n" + "=" * 70)
    print("Examples Complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
