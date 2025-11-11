#!/usr/bin/env python3
"""
Comprehensive Test Runner for WorkflowOrchestrator.list_available_templates()

Runs all tests and generates a comprehensive report.
"""

import subprocess
import sys


def run_command(cmd, description):
    """Run a command and capture output"""
    print(f"\n{'=' * 70}")
    print(f"{description}")
    print('=' * 70)

    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, cwd="/home/user/claude-analyst/semantic-layer"
    )

    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    return result.returncode == 0


def main():
    """Run all tests and generate report"""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE TEST REPORT")
    print("WorkflowOrchestrator.list_available_templates()")
    print("=" * 70)

    results = {}

    # Test 1: Unit Tests
    print("\n📝 Running Unit Tests (20 tests)...")
    results['unit_tests'] = run_command(
        "uv run python test_workflow_orchestrator_fix.py",
        "Unit Tests: Test-Driven Development Suite"
    )

    # Test 2: Integration Tests
    print("\n🔗 Running Integration Tests (5 tests)...")
    results['integration_tests'] = run_command(
        "uv run python test_list_templates_integration.py",
        "Integration Tests: System Compatibility"
    )

    # Test 3: Verification
    print("\n✅ Running Verification Script...")
    results['verification'] = run_command(
        "uv run python verify_list_templates.py",
        "Verification: Template Discovery Output"
    )

    # Test 4: Usage Examples
    print("\n📚 Running Usage Examples...")
    results['examples'] = run_command(
        "uv run python examples/list_templates_usage.py",
        "Usage Examples: 7 Real-World Scenarios"
    )

    # Final Report
    print("\n" + "=" * 70)
    print("FINAL TEST REPORT")
    print("=" * 70 + "\n")

    total_passed = sum(1 for v in results.values() if v)
    total_tests = len(results)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status:12} - {test_name.replace('_', ' ').title()}")

    print("\n" + "=" * 70)
    print(f"Overall Result: {total_passed}/{total_tests} test suites passed")
    print("=" * 70 + "\n")

    if total_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Implementation is complete and verified.")
        print("\nTest Coverage:")
        print("  • 20 Unit Tests ✅")
        print("  • 5 Integration Tests ✅")
        print("  • Template Discovery Verification ✅")
        print("  • 7 Usage Examples ✅")
        print("\nReady for:")
        print("  • MCP Server Integration")
        print("  • Claude Desktop Deployment")
        print("  • Production Use")
        return 0
    else:
        print("❌ Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
