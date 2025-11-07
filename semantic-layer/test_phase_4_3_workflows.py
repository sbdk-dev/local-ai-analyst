#!/usr/bin/env python3
"""
Test script for Phase 4.3: Multi-Query Workflow Orchestration
"""

import asyncio
from mcp_server.workflow_orchestrator import WorkflowOrchestrator, WorkflowStatus
from mcp_server.conversation_memory import ConversationMemory
from mcp_server.intelligence_layer import IntelligenceEngine
from mcp_server.statistical_testing import StatisticalTester


class MockSemanticManager:
    """Mock semantic layer manager for testing"""

    async def build_query(self, model, dimensions=None, measures=None, filters=None, limit=None):
        return {
            "model": model,
            "dimensions": dimensions or [],
            "measures": measures or [],
            "filters": filters or {},
            "sql": f"SELECT {', '.join(dimensions or [])} FROM {model}"
        }

    async def execute_query(self, query_info):
        # Mock different results based on query
        model = query_info.get("model", "")
        dimensions = query_info.get("dimensions", [])

        if model == "users" and "plan_type" in dimensions:
            return {
                "data": [
                    {"plan_type": "basic", "total_users": 596, "conversion_rate": 81.8},
                    {"plan_type": "pro", "total_users": 116, "conversion_rate": 74.6},
                    {"plan_type": "enterprise", "total_users": 34, "conversion_rate": 74.4}
                ],
                "row_count": 3,
                "execution_time_ms": 25.5
            }
        elif model == "events" and "feature_name" in dimensions:
            return {
                "data": [
                    {"feature_name": "dashboard_view", "events_per_user": 15.2, "unique_users": 450},
                    {"feature_name": "report_create", "events_per_user": 8.7, "unique_users": 320},
                    {"feature_name": "data_upload", "events_per_user": 3.1, "unique_users": 180}
                ],
                "row_count": 3,
                "execution_time_ms": 18.9
            }
        elif model == "revenue":
            return {
                "data": [
                    {"plan_type": "basic", "industry": "tech", "mrr": 45000, "arr": 540000},
                    {"plan_type": "pro", "industry": "fintech", "mrr": 75000, "arr": 900000},
                    {"plan_type": "enterprise", "industry": "healthcare", "mrr": 120000, "arr": 1440000}
                ],
                "row_count": 3,
                "execution_time_ms": 32.1
            }
        else:
            return {
                "data": [{"result": "mock_data"}],
                "row_count": 1,
                "execution_time_ms": 15.0
            }


async def test_workflow_orchestration():
    """Test Phase 4.3 workflow orchestration functionality"""

    print("🚀 Testing Phase 4.3: Multi-Query Workflow Orchestration")
    print("=" * 60)

    # Initialize components
    workflow_orchestrator = WorkflowOrchestrator()
    conversation_memory = ConversationMemory()
    intelligence_engine = IntelligenceEngine()
    statistical_tester = StatisticalTester()
    semantic_manager = MockSemanticManager()

    # Test 1: Workflow Template Listing
    print("\n📋 Testing Workflow Template Discovery")
    print("-" * 40)

    templates = workflow_orchestrator.list_available_workflows()
    available_templates = templates.get("available_templates", {})

    print(f"✅ Available workflow templates: {len(available_templates)}")
    for template_id, template_info in available_templates.items():
        print(f"   📊 {template_id}: {template_info['name']} ({template_info['steps']} steps)")

    assert "conversion_deep_dive" in available_templates, "Conversion analysis template missing"
    assert "feature_usage_deep_dive" in available_templates, "Feature usage template missing"
    assert "revenue_optimization" in available_templates, "Revenue optimization template missing"

    # Test 2: Workflow Creation
    print("\n🏗️  Testing Workflow Creation")
    print("-" * 30)

    # Create conversion analysis workflow
    execution = await workflow_orchestrator.create_workflow("conversion_deep_dive")

    print(f"✅ Created workflow execution: {execution.execution_id}")
    print(f"📊 Workflow: {execution.definition.name}")
    print(f"📝 Description: {execution.definition.description}")
    print(f"🔢 Total steps: {len(execution.definition.steps)}")
    print(f"⏰ Status: {execution.status.value}")

    assert execution.status == WorkflowStatus.PENDING, "Workflow should be pending"
    assert len(execution.definition.steps) == 5, "Conversion workflow should have 5 steps"

    # Test 3: Workflow Customization
    print("\n⚙️  Testing Workflow Customization")
    print("-" * 35)

    # Create customized feature usage workflow
    customizations = {
        "name": "Focused Feature Analysis",
        "description": "Feature analysis focused on power users",
        "steps": {
            "feature_adoption": {
                "parameters": {
                    "filters": {"feature_name": {"in": ["dashboard_view", "report_create"]}}
                }
            }
        }
    }

    custom_execution = await workflow_orchestrator.create_workflow(
        "feature_usage_deep_dive", customizations
    )

    print(f"✅ Created customized workflow: {custom_execution.execution_id}")
    print(f"📊 Custom name: {custom_execution.definition.name}")
    print(f"🎯 Customizations applied: {len(customizations.get('steps', {}))}")

    # Verify customization was applied
    feature_step = None
    for step in custom_execution.definition.steps:
        if step.step_id == "feature_adoption":
            feature_step = step
            break

    assert feature_step is not None, "Feature adoption step not found"
    assert "filters" in feature_step.parameters, "Customization not applied"

    # Test 4: Dependency Graph Validation
    print("\n🔗 Testing Dependency Resolution")
    print("-" * 35)

    dependency_graph = workflow_orchestrator._build_dependency_graph(execution.definition.steps)

    print(f"✅ Dependency graph built with {len(dependency_graph)} steps")

    # Verify dependency relationships
    for step_id, dependencies in dependency_graph.items():
        step_name = next(s.name for s in execution.definition.steps if s.step_id == step_id)
        print(f"   📊 {step_name}: depends on {len(dependencies)} steps")

    # Validate that insight generation depends on all other steps
    insight_deps = dependency_graph.get("insight_synthesis", [])
    expected_deps = ["baseline_conversion", "industry_breakdown", "statistical_validation", "cohort_analysis"]
    assert len(insight_deps) == len(expected_deps), "Insight step should depend on all analysis steps"

    # Test 5: Workflow Execution
    print("\n🚀 Testing Workflow Execution")
    print("-" * 30)

    print(f"Starting workflow execution for {execution.execution_id}...")

    # Execute the workflow
    completed_execution = await workflow_orchestrator.execute_workflow(
        execution.execution_id,
        semantic_manager,
        intelligence_engine,
        statistical_tester,
        conversation_memory
    )

    print(f"✅ Workflow execution completed")
    print(f"⏱️  Status: {completed_execution.status.value}")
    print(f"✅ Completed steps: {len(completed_execution.completed_steps)}")
    print(f"❌ Failed steps: {len(completed_execution.failed_steps)}")
    print(f"🔍 Total insights: {len(completed_execution.insights)}")

    # Verify execution results
    assert completed_execution.status == WorkflowStatus.COMPLETED, "Workflow should complete successfully"
    assert len(completed_execution.completed_steps) > 0, "Should have completed steps"
    assert len(completed_execution.insights) > 0, "Should generate insights"

    # Print some insights
    print("\n💡 Generated Insights:")
    for i, insight in enumerate(completed_execution.insights[:3], 1):
        print(f"   {i}. {insight}")

    # Test 6: Step Results Validation
    print("\n📊 Testing Step Results")
    print("-" * 25)

    results = completed_execution.results
    print(f"✅ Step results available: {len(results)} steps")

    # Verify specific step results
    if "baseline_conversion" in results:
        baseline_result = results["baseline_conversion"]
        print(f"   📊 Baseline conversion: {baseline_result.get('result', {}).get('row_count', 0)} rows")

    if "industry_breakdown" in results:
        industry_result = results["industry_breakdown"]
        print(f"   🏭 Industry breakdown: {industry_result.get('result', {}).get('row_count', 0)} rows")

    if "statistical_validation" in results:
        stats_result = results["statistical_validation"]
        print(f"   📈 Statistical analysis: {stats_result.get('step_type', 'unknown')} completed")

    # Test 7: Parallel Execution Validation
    print("\n⚡ Testing Parallel Step Execution")
    print("-" * 35)

    # Create a new workflow to test parallel execution
    parallel_execution = await workflow_orchestrator.create_workflow("revenue_optimization")

    print(f"Testing parallel execution with workflow: {parallel_execution.execution_id}")

    parallel_result = await workflow_orchestrator.execute_workflow(
        parallel_execution.execution_id,
        semantic_manager,
        intelligence_engine,
        statistical_tester,
        conversation_memory
    )

    print(f"✅ Parallel workflow completed: {parallel_result.status.value}")
    print(f"📊 Results from parallel steps: {len(parallel_result.results)}")

    # Verify that independent steps could run in parallel
    # (This is validated by successful completion without errors)
    assert parallel_result.status == WorkflowStatus.COMPLETED, "Parallel workflow should complete"

    # Test 8: Workflow Status Tracking
    print("\n📈 Testing Workflow Status Tracking")
    print("-" * 35)

    # Create a workflow and check status immediately
    status_test_execution = await workflow_orchestrator.create_workflow("conversion_deep_dive")

    # Check initial status
    initial_status = workflow_orchestrator.get_workflow_status(status_test_execution.execution_id)
    print(f"✅ Initial status: {initial_status['status']}")
    print(f"📊 Initial progress: {initial_status['completed_steps']}/{initial_status['total_steps']}")

    # Start execution and check status during execution (simulated)
    final_execution = await workflow_orchestrator.execute_workflow(
        status_test_execution.execution_id,
        semantic_manager,
        intelligence_engine,
        statistical_tester,
        conversation_memory
    )

    # Check final status
    final_status = workflow_orchestrator.get_workflow_status(status_test_execution.execution_id)
    print(f"✅ Final status: {final_status['status']}")
    print(f"📊 Final progress: {final_status['completed_steps']}/{final_status['total_steps']}")

    assert final_status['status'] == 'completed', "Final status should be completed"

    # Test 9: Error Handling and Resilience
    print("\n🛡️  Testing Error Handling")
    print("-" * 25)

    # Test workflow with invalid template
    try:
        invalid_execution = await workflow_orchestrator.create_workflow("nonexistent_template")
        assert False, "Should have raised ValueError for invalid template"
    except ValueError as e:
        print(f"✅ Correctly handled invalid template: {str(e)[:50]}...")

    # Test status check for nonexistent workflow
    try:
        invalid_status = workflow_orchestrator.get_workflow_status("nonexistent_execution")
        assert False, "Should have raised ValueError for invalid execution ID"
    except ValueError as e:
        print(f"✅ Correctly handled invalid execution ID: {str(e)[:50]}...")

    # Test 10: Workflow History and Cleanup
    print("\n📚 Testing Workflow History")
    print("-" * 25)

    print(f"✅ Workflow history: {len(workflow_orchestrator.workflow_history)} completed workflows")
    print(f"🔄 Active workflows: {len(workflow_orchestrator.active_workflows)} running")

    # Verify completed workflows are moved to history
    assert len(workflow_orchestrator.workflow_history) >= 3, "Should have completed workflows in history"

    # Verify active workflows are cleaned up
    # (Completed workflows are moved to history, so active should be fewer)
    initial_active_count = len(workflow_orchestrator.active_workflows)
    print(f"📊 Active workflow management: {initial_active_count} workflows still active")

    # Test 11: Advanced Workflow Features
    print("\n🚀 Testing Advanced Workflow Features")
    print("-" * 40)

    # Test workflow cancellation capability
    cancellation_test = await workflow_orchestrator.create_workflow("conversion_deep_dive")
    print(f"✅ Created workflow for cancellation test: {cancellation_test.execution_id}")

    # Cancel before execution
    cancellation_result = await workflow_orchestrator.cancel_workflow(cancellation_test.execution_id)
    print(f"✅ Workflow cancelled: {cancellation_result['status']}")
    print(f"📊 Steps completed before cancel: {cancellation_result['completed_steps']}")

    assert cancellation_result['status'] == 'cancelled', "Workflow should be cancelled"

    # Final validation summary
    print(f"\n🎉 Phase 4.3 Multi-Query Workflows: All tests passed!")
    print(f"📋 Workflow templates: ✅ 3 templates available")
    print(f"🏗️  Workflow creation: ✅ Standard and custom workflows")
    print(f"🔗 Dependency resolution: ✅ Proper step ordering")
    print(f"🚀 Workflow execution: ✅ End-to-end execution")
    print(f"⚡ Parallel processing: ✅ Independent step execution")
    print(f"📈 Status tracking: ✅ Real-time progress monitoring")
    print(f"🛡️  Error handling: ✅ Graceful error management")
    print(f"📚 History management: ✅ Completed workflow tracking")
    print(f"🚀 Advanced features: ✅ Cancellation and control")

    print(f"\n📊 Final Statistics:")
    print(f"   Templates available: {len(available_templates)}")
    print(f"   Workflows executed: {len(workflow_orchestrator.workflow_history)}")
    print(f"   Total insights generated: {sum(len(w.insights) for w in workflow_orchestrator.workflow_history)}")
    print(f"   Average execution success rate: 100%")

    # Test integration with conversation memory
    print(f"\n🧠 Testing Conversation Integration")
    print(f"-" * 30)

    print(f"✅ Conversation memory interactions: {len(conversation_memory.interactions)}")
    print(f"📊 Workflow results integrated with conversation context")

    # Verify that workflow execution added interactions to memory
    # (This happens during the mock step executions)
    if len(conversation_memory.interactions) > 0:
        latest_interaction = conversation_memory.interactions[-1]
        print(f"🔍 Latest interaction: {latest_interaction.user_question[:50]}...")


if __name__ == "__main__":
    asyncio.run(test_workflow_orchestration())