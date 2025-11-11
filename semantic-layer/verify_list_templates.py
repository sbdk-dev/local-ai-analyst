#!/usr/bin/env python3
"""
Verification script to see the actual output of list_available_templates()
"""

import json
from mcp_server.workflow_orchestrator import WorkflowOrchestrator


def main():
    print("=" * 70)
    print("Verifying list_available_templates() Output")
    print("=" * 70 + "\n")

    orchestrator = WorkflowOrchestrator()
    templates = orchestrator.list_available_templates()

    print(f"Total templates: {len(templates)}\n")
    print(json.dumps(templates, indent=2))

    print("\n" + "=" * 70)
    print("Summary:")
    print("=" * 70)
    for template in templates:
        print(f"\n📋 {template['name']}")
        print(f"   Steps: {template['steps']}")
        print(f"   Step Types: {', '.join(template['step_types'])}")
        print(f"   Duration: {template['estimated_duration']}")
        print(f"   Use Cases: {len(template['use_cases'])} defined")


if __name__ == "__main__":
    main()
