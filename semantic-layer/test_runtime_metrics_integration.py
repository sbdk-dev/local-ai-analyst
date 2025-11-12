#!/usr/bin/env python3
"""
Integration tests for Runtime Metrics MCP Tools

Tests the 3 new MCP tools:
1. define_custom_metric
2. list_custom_metrics
3. delete_custom_metric
"""

import asyncio
import json
import logging
import shutil
import sys
import tempfile
from pathlib import Path

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_mcp_tools_integration():
    """Test the runtime metrics MCP tools"""

    print("\n" + "=" * 70)
    print("RUNTIME METRICS MCP TOOLS INTEGRATION TEST")
    print("=" * 70 + "\n")

    passed = 0
    failed = 0

    # Setup: Create temporary environment
    temp_dir = tempfile.mkdtemp()
    temp_data_dir = Path(temp_dir) / "data"
    temp_data_dir.mkdir(parents=True, exist_ok=True)
    temp_metrics_file = temp_data_dir / "runtime_metrics.json"

    try:
        # Import modules
        sys.path.insert(0, str(Path(__file__).parent))
        from mcp_server.runtime_metrics import RuntimeMetricRegistry, get_registry
        from mcp_server.semantic_layer_integration import SemanticLayerManager

        # Initialize components
        print("[Setup] Initializing semantic layer manager...")
        semantic_manager = SemanticLayerManager()
        await semantic_manager.initialize()
        print("✓ Semantic layer initialized\n")

        # Initialize runtime metrics registry
        print("[Setup] Initializing runtime metrics registry...")
        registry = RuntimeMetricRegistry(temp_metrics_file)
        print("✓ Runtime metrics registry initialized\n")

        # Test 1: Define a count_distinct metric
        print("[Test 1/6] Testing define_custom_metric (count_distinct)...")
        try:
            result = await registry.define_metric(
                name="power_users",
                type="count_distinct",
                model="users",
                semantic_manager=semantic_manager,
                description="Users with high engagement",
                dimension="user_id",
                filters={"login_count__gt": 100},
                tags=["engagement", "core"],
            )

            assert result["status"] == "success", f"Failed: {result.get('error')}"
            assert result["metric"]["name"] == "power_users"
            assert result["metric"]["type"] == "count_distinct"
            assert result["metric"]["dimension"] == "user_id"
            assert "engagement" in result["metric"]["tags"]

            print("✓ PASSED: define_custom_metric (count_distinct)")
            passed += 1
        except Exception as e:
            print(f"✗ FAILED: define_custom_metric (count_distinct) - {str(e)}")
            failed += 1

        # Test 2: Define a ratio metric
        print("\n[Test 2/6] Testing define_custom_metric (ratio)...")
        try:
            result = await registry.define_metric(
                name="conversion_rate",
                type="ratio",
                model="users",
                semantic_manager=semantic_manager,
                description="Conversion rate from free to paid",
                numerator="paid_users",
                denominator="total_users",
                tags=["conversion"],
            )

            assert result["status"] == "success", f"Failed: {result.get('error')}"
            assert result["metric"]["type"] == "ratio"
            assert result["metric"]["numerator"] == "paid_users"
            assert result["metric"]["denominator"] == "total_users"

            print("✓ PASSED: define_custom_metric (ratio)")
            passed += 1
        except Exception as e:
            print(f"✗ FAILED: define_custom_metric (ratio) - {str(e)}")
            failed += 1

        # Test 3: Define a custom SQL metric
        print("\n[Test 3/6] Testing define_custom_metric (custom_sql)...")
        try:
            result = await registry.define_metric(
                name="avg_revenue_per_user",
                type="custom_sql",
                model="users",
                semantic_manager=semantic_manager,
                description="Average revenue per user",
                sql="SUM(revenue) / COUNT(DISTINCT user_id)",
                tags=["revenue"],
            )

            assert result["status"] == "success", f"Failed: {result.get('error')}"
            assert result["metric"]["type"] == "custom_sql"
            assert "SUM(revenue)" in result["metric"]["sql"]

            print("✓ PASSED: define_custom_metric (custom_sql)")
            passed += 1
        except Exception as e:
            print(f"✗ FAILED: define_custom_metric (custom_sql) - {str(e)}")
            failed += 1

        # Test 4: List all custom metrics
        print("\n[Test 4/6] Testing list_custom_metrics (all)...")
        try:
            metrics = registry.list_metrics()

            assert len(metrics) == 3, f"Expected 3 metrics, found {len(metrics)}"
            metric_names = [m.name for m in metrics]
            assert "power_users" in metric_names
            assert "conversion_rate" in metric_names
            assert "avg_revenue_per_user" in metric_names

            print(f"✓ PASSED: list_custom_metrics (found {len(metrics)} metrics)")
            passed += 1
        except Exception as e:
            print(f"✗ FAILED: list_custom_metrics (all) - {str(e)}")
            failed += 1

        # Test 5: List custom metrics by model
        print("\n[Test 5/6] Testing list_custom_metrics (filtered by model)...")
        try:
            user_metrics = registry.list_metrics(model="users")

            assert len(user_metrics) == 3, f"Expected 3 user metrics, found {len(user_metrics)}"

            print(f"✓ PASSED: list_custom_metrics (filtered by model)")
            passed += 1
        except Exception as e:
            print(f"✗ FAILED: list_custom_metrics (filtered by model) - {str(e)}")
            failed += 1

        # Test 6: Delete a custom metric
        print("\n[Test 6/6] Testing delete_custom_metric...")
        try:
            result = await registry.delete_metric("avg_revenue_per_user")

            assert result["status"] == "success", f"Failed: {result.get('error')}"

            # Verify deletion
            remaining_metrics = registry.list_metrics()
            assert len(remaining_metrics) == 2, f"Expected 2 metrics, found {len(remaining_metrics)}"
            metric_names = [m.name for m in remaining_metrics]
            assert "avg_revenue_per_user" not in metric_names

            print("✓ PASSED: delete_custom_metric")
            passed += 1
        except Exception as e:
            print(f"✗ FAILED: delete_custom_metric - {str(e)}")
            failed += 1

        # Test 7: Persistence check
        print("\n[Test 7/7] Testing metric persistence...")
        try:
            # Create new registry instance (simulates server restart)
            registry2 = RuntimeMetricRegistry(temp_metrics_file)

            loaded_metrics = registry2.list_metrics()
            assert len(loaded_metrics) == 2, f"Expected 2 persisted metrics, found {len(loaded_metrics)}"

            metric_names = [m.name for m in loaded_metrics]
            assert "power_users" in metric_names
            assert "conversion_rate" in metric_names

            print("✓ PASSED: metric persistence")
            passed += 1
        except Exception as e:
            print(f"✗ FAILED: metric persistence - {str(e)}")
            failed += 1

        # Print results
        print("\n" + "=" * 70)
        print(f"INTEGRATION TEST RESULTS: {passed} passed, {failed} failed out of 7 tests")
        print("=" * 70 + "\n")

        if failed == 0:
            print("✅ ALL INTEGRATION TESTS PASSED!")
            return True
        else:
            print(f"❌ {failed} INTEGRATION TEST(S) FAILED")
            return False

    except Exception as e:
        print(f"\n❌ INTEGRATION TEST SUITE FAILED: {str(e)}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Cleanup
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir)
        print("\n[Cleanup] Temporary files removed")


if __name__ == "__main__":
    success = asyncio.run(test_mcp_tools_integration())
    exit(0 if success else 1)
