#!/usr/bin/env python3
"""
Comprehensive test of all 22 MCP tools to verify production readiness.
"""

import asyncio
import traceback
from datetime import datetime

# Import all the MCP tool functions directly
from mcp_server.server import (cancel_workflow, clear_query_cache,
                               conversation_memory, create_workflow,
                               execute_workflow, export_conversation_summary,
                               get_contextual_suggestions,
                               get_conversation_context, get_model,
                               get_optimization_dashboard,
                               get_query_performance, get_sample_queries,
                               get_workflow_status, health_check, list_models,
                               list_workflow_templates, mcp, optimize_query,
                               query_model, query_optimizer,
                               run_conversion_analysis,
                               run_feature_usage_analysis, semantic_manager,
                               suggest_analysis, suggest_batch_queries,
                               test_significance, workflow_orchestrator)


async def test_tool(tool_name: str, tool_func, *args, **kwargs):
    """Test a single MCP tool and return results"""
    try:
        print(f"🧪 Testing {tool_name}...", end=" ")
        result = await tool_func(*args, **kwargs)

        # Basic validation
        if result is None:
            print("❌ FAILED - returned None")
            return False
        elif isinstance(result, dict) and "error" in result:
            if result.get("error"):
                print(f"❌ FAILED - {result.get('message', 'Unknown error')}")
                return False
            else:
                print("✅ PASSED")
                return True
        else:
            print("✅ PASSED")
            return True

    except Exception as e:
        print(f"❌ FAILED - {str(e)}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False


async def main():
    print("🚀 Testing All 22 MCP Tools - Production Readiness Verification")
    print("=" * 70)

    # Initialize the components
    await semantic_manager._load_models()

    tests_passed = 0
    tests_failed = 0

    print("\n📋 1. DISCOVERY & INFORMATION TOOLS")
    print("-" * 50)

    # 1. list_models
    if await test_tool("list_models", list_models):
        tests_passed += 1
    else:
        tests_failed += 1

    # 2. get_model
    if await test_tool("get_model", get_model, model_name="users"):
        tests_passed += 1
    else:
        tests_failed += 1

    # 3. health_check
    if await test_tool("health_check", health_check):
        tests_passed += 1
    else:
        tests_failed += 1

    # 4. get_sample_queries
    if await test_tool("get_sample_queries", get_sample_queries, model_name="users"):
        tests_passed += 1
    else:
        tests_failed += 1

    print("\n📊 2. CORE QUERY TOOLS")
    print("-" * 50)

    # 5. query_model
    if await test_tool(
        "query_model",
        query_model,
        model="users",
        dimensions=["plan_type"],
        measures=["total_users"],
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # 6. suggest_analysis
    if await test_tool(
        "suggest_analysis",
        suggest_analysis,
        current_result="Sample result",
        context="testing",
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # 7. test_significance
    sample_data = {
        "data": [
            {"plan_type": "free", "total_users": 100},
            {"plan_type": "pro", "total_users": 200},
        ]
    }
    if await test_tool(
        "test_significance",
        test_significance,
        data=sample_data,
        comparison_dimension="plan_type",
        metric="total_users",
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    print("\n🧠 3. CONVERSATION MEMORY TOOLS")
    print("-" * 50)

    # 8. get_conversation_context
    if await test_tool("get_conversation_context", get_conversation_context):
        tests_passed += 1
    else:
        tests_failed += 1

    # 9. get_contextual_suggestions
    if await test_tool("get_contextual_suggestions", get_contextual_suggestions):
        tests_passed += 1
    else:
        tests_failed += 1

    # 10. export_conversation_summary
    if await test_tool("export_conversation_summary", export_conversation_summary):
        tests_passed += 1
    else:
        tests_failed += 1

    print("\n⚡ 4. QUERY OPTIMIZATION TOOLS")
    print("-" * 50)

    # 11. optimize_query
    query_info = {
        "model": "users",
        "dimensions": ["plan_type"],
        "measures": ["total_users"],
    }
    if await test_tool("optimize_query", optimize_query, query_info=query_info):
        tests_passed += 1
    else:
        tests_failed += 1

    # 12. get_query_performance
    if await test_tool("get_query_performance", get_query_performance):
        tests_passed += 1
    else:
        tests_failed += 1

    # 13. suggest_batch_queries
    pending_queries = [query_info]
    if await test_tool(
        "suggest_batch_queries", suggest_batch_queries, pending_queries=pending_queries
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # 14. clear_query_cache
    if await test_tool("clear_query_cache", clear_query_cache):
        tests_passed += 1
    else:
        tests_failed += 1

    # 15. get_optimization_dashboard
    if await test_tool("get_optimization_dashboard", get_optimization_dashboard):
        tests_passed += 1
    else:
        tests_failed += 1

    print("\n🔄 5. WORKFLOW ORCHESTRATION TOOLS")
    print("-" * 50)

    # 16. list_workflow_templates
    if await test_tool("list_workflow_templates", list_workflow_templates):
        tests_passed += 1
    else:
        tests_failed += 1

    # 17. create_workflow
    workflow_result = await create_workflow(template_id="conversion_deep_dive")
    if workflow_result and not workflow_result.get("error"):
        print("🧪 Testing create_workflow... ✅ PASSED")
        tests_passed += 1
        workflow_id = workflow_result["execution_id"]

        # 18. get_workflow_status
        if await test_tool(
            "get_workflow_status", get_workflow_status, execution_id=workflow_id
        ):
            tests_passed += 1
        else:
            tests_failed += 1

        # 19. cancel_workflow
        if await test_tool(
            "cancel_workflow", cancel_workflow, execution_id=workflow_id
        ):
            tests_passed += 1
        else:
            tests_failed += 1
    else:
        print("🧪 Testing create_workflow... ❌ FAILED")
        tests_failed += 1
        # Skip dependent tests
        print(
            "🧪 Testing get_workflow_status... ⚠️ SKIPPED (depends on create_workflow)"
        )
        print("🧪 Testing cancel_workflow... ⚠️ SKIPPED (depends on create_workflow)")
        tests_failed += 2

    # 20. execute_workflow (Create fresh workflow for execution test)
    fresh_workflow = await create_workflow(template_id="conversion_deep_dive")
    if fresh_workflow and not fresh_workflow.get("error"):
        execution_id = fresh_workflow["execution_id"]
        if await test_tool(
            "execute_workflow", execute_workflow, execution_id=execution_id
        ):
            tests_passed += 1
        else:
            tests_failed += 1
    else:
        print("🧪 Testing execute_workflow... ⚠️ SKIPPED (workflow creation failed)")
        tests_failed += 1

    print("\n📈 6. SPECIALIZED WORKFLOW TOOLS")
    print("-" * 50)

    # 21. run_conversion_analysis
    if await test_tool("run_conversion_analysis", run_conversion_analysis):
        tests_passed += 1
    else:
        tests_failed += 1

    # 22. run_feature_usage_analysis
    if await test_tool("run_feature_usage_analysis", run_feature_usage_analysis):
        tests_passed += 1
    else:
        tests_failed += 1

    # Final Results
    print("\n🎯 FINAL RESULTS")
    print("=" * 70)
    total_tools = tests_passed + tests_failed
    success_rate = (tests_passed / total_tools * 100) if total_tools > 0 else 0

    print(f"📊 Total MCP Tools Tested: {total_tools}")
    print(f"✅ Tests Passed: {tests_passed}")
    print(f"❌ Tests Failed: {tests_failed}")
    print(f"📈 Success Rate: {success_rate:.1f}%")

    if tests_failed == 0:
        print("\n🎉 ALL MCP TOOLS WORKING! System is 100% production ready!")
        return True
    else:
        print(
            f"\n⚠️ {tests_failed} tools have issues that need fixing before production deployment."
        )
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
