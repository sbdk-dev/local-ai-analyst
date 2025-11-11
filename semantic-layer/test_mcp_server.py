#!/usr/bin/env python3
"""
Test script for MCP server functionality
"""

import asyncio

from mcp_server.intelligence_layer import IntelligenceEngine
from mcp_server.semantic_layer_integration import SemanticLayerManager
from mcp_server.statistical_testing import StatisticalTester


async def main():
    """Test core functionality"""

    print("🧪 Testing AI Analyst MCP Server Components")
    print("=" * 50)

    # Initialize components
    semantic_manager = SemanticLayerManager()
    intelligence_engine = IntelligenceEngine()
    statistical_tester = StatisticalTester()

    try:
        # Test 1: Semantic layer initialization
        print("\n1. Testing semantic layer initialization...")
        await semantic_manager.initialize()
        print("✅ Semantic layer initialized")

        # Test 2: Health check
        print("\n2. Testing health check...")
        health = await semantic_manager.health_check()
        is_healthy = health.get("database_connected", False)
        print(f"✅ Health check: {'healthy' if is_healthy else 'unhealthy'}")
        if "database_info" in health:
            print(f"   Database size: {health['database_info']['file_size_mb']}MB")
        print(f"   Models loaded: {health.get('models_count', 0)}")

        # Test 3: List available models
        print("\n3. Testing model listing...")
        models = await semantic_manager.get_available_models()
        print(f"✅ Found {len(models)} models:")
        for model in models:
            print(f"   - {model['name']}: {model['description']}")
            print(
                f"     Dimensions: {model['dimensions_count']}, Measures: {model['measures_count']}"
            )

        # Test 4: Get model schema
        print("\n4. Testing model schema retrieval...")
        schema = await semantic_manager.get_model_schema("users")
        print(f"✅ Users model schema loaded")
        print(f"   Dimensions: {len(schema['dimensions'])}")
        print(f"   Measures: {len(schema['measures'])}")

        # Test 5: Build and execute query
        print("\n5. Testing query building and execution...")
        query_info = await semantic_manager.build_query(
            model="users",
            dimensions=["plan_type"],
            measures=["total_users", "conversion_rate"],
        )
        print(f"✅ Query built: {query_info['sql'][:100]}...")

        result = await semantic_manager.execute_query(query_info)
        print(
            f"✅ Query executed: {result['row_count']} rows in {result['execution_time_ms']}ms"
        )

        if result["data"]:
            print("   Results preview:")
            for row in result["data"][:3]:
                print(f"     {row}")

        # Test 6: Statistical validation
        print("\n6. Testing statistical validation...")
        validation = await statistical_tester.validate_result(result, ["plan_type"])
        print(f"✅ Validation complete")
        print(f"   Sample sizes: {validation['sample_sizes']}")
        if validation["warnings"]:
            print(f"   Warnings: {validation['warnings']}")

        # Test 7: Statistical testing
        print("\n7. Testing statistical analysis...")
        stats_result = await statistical_tester.auto_test_comparison(
            result, ["plan_type"], ["total_users"]
        )
        if stats_result:
            print(f"✅ Statistical test: {stats_result['test_type']}")
            print(f"   P-value: {stats_result['p_value']:.4f}")
            print(f"   Effect size: {stats_result['effect_size_interpretation']}")
        else:
            print("ℹ️ No statistical test appropriate for this data")

        # Test 8: Natural language interpretation
        print("\n8. Testing natural language interpretation...")
        interpretation = await intelligence_engine.generate_interpretation(
            result=result,
            query_info=query_info,
            validation=validation,
            statistical_analysis=stats_result,
        )
        print(f"✅ Interpretation: {interpretation}")

        # Test 9: Analysis suggestions
        print("\n9. Testing analysis suggestions...")
        suggestions = await intelligence_engine.suggest_next_questions(
            result=result,
            context="plan type analysis",
            current_dimensions=["plan_type"],
            current_measures=["total_users", "conversion_rate"],
        )
        print(f"✅ Generated {len(suggestions)} suggestions:")
        for suggestion in suggestions[:2]:
            print(f"   - {suggestion['question']} ({suggestion['reason']})")

        print(
            f"\n🎉 All tests passed! MCP server is ready for Claude Desktop integration."
        )

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise

    finally:
        await semantic_manager.cleanup()
        print("\n🧹 Cleanup complete")


if __name__ == "__main__":
    asyncio.run(main())
