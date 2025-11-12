#!/usr/bin/env python3
"""
Standalone tests for Runtime Metrics System (no mcp_server imports)

This bypasses the mcp_server package import to avoid loading all dependencies.
"""

import asyncio
import json
import logging
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Add parent directory to path for direct module import
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Import runtime_metrics directly (not through mcp_server package)
# This will work since we're adding the path
from mcp_server import runtime_metrics


# Test fixtures and mocks
class MockSemanticManager:
    """Mock semantic layer manager for testing"""

    async def get_available_models(self):
        """Return mock models"""
        return [
            {
                "name": "users",
                "description": "User analytics",
                "table": "users",
                "dimensions": ["user_id", "plan_type", "industry"],
                "measures": ["total_users", "avg_ltv"],
            },
            {
                "name": "events",
                "description": "Event tracking",
                "table": "events",
                "dimensions": ["event_type", "user_id", "date"],
                "measures": ["total_events", "unique_users"],
            },
        ]

    async def get_model_schema(self, model_name: str):
        """Return mock model schema"""
        if model_name == "users":
            return {
                "name": "users",
                "dimensions": [
                    {"name": "user_id", "type": "string"},
                    {"name": "plan_type", "type": "string"},
                    {"name": "industry", "type": "string"},
                    {"name": "signup_date", "type": "date"},
                ],
                "measures": [
                    {"name": "total_users", "type": "count"},
                    {"name": "avg_ltv", "type": "avg"},
                ],
            }
        elif model_name == "events":
            return {
                "name": "events",
                "dimensions": [
                    {"name": "event_type", "type": "string"},
                    {"name": "user_id", "type": "string"},
                    {"name": "date", "type": "date"},
                ],
                "measures": [
                    {"name": "total_events", "type": "count"},
                    {"name": "unique_users", "type": "count_distinct"},
                ],
            }
        else:
            raise ValueError(f"Unknown model: {model_name}")


async def run_all_tests():
    """Run all runtime metrics tests"""

    print("\n" + "=" * 60)
    print("RUNTIME METRICS TEST SUITE (Standalone)")
    print("=" * 60 + "\n")

    passed = 0
    failed = 0

    # Test 1: Basic metric creation
    print("\n[1/15] Testing basic metric creation...")
    try:
        temp_storage = Path(tempfile.mkdtemp()) / "test_metrics.json"
        mock_manager = MockSemanticManager()

        registry = runtime_metrics.RuntimeMetricRegistry(temp_storage)

        result = await registry.define_metric(
            name="power_users",
            type="count_distinct",
            model="users",
            semantic_manager=mock_manager,
            description="Users with 100+ logins",
            dimension="user_id",
            filters={"login_count__gt": 100},
            tags=["engagement", "power_users"],
        )

        assert result["status"] == "success", f"Failed: {result.get('error')}"
        assert result["metric"]["name"] == "power_users"
        assert result["metric"]["type"] == "count_distinct"
        print("✓ PASSED: Basic metric creation")
        passed += 1
        shutil.rmtree(temp_storage.parent)
    except Exception as e:
        print(f"✗ FAILED: Basic metric creation - {str(e)}")
        failed += 1

    # Test 2: Metric persistence
    print("\n[2/15] Testing metric persistence...")
    try:
        temp_storage = Path(tempfile.mkdtemp()) / "test_metrics.json"
        mock_manager = MockSemanticManager()

        # Create registry and add metric
        registry1 = runtime_metrics.RuntimeMetricRegistry(temp_storage)
        await registry1.define_metric(
            name="active_users",
            type="count_distinct",
            model="users",
            semantic_manager=mock_manager,
            dimension="user_id",
            filters={"last_login__gte": "2024-01-01"},
        )

        # Create new registry (simulates restart)
        registry2 = runtime_metrics.RuntimeMetricRegistry(temp_storage)

        metric = registry2.get_metric("active_users")
        assert metric is not None, "Metric not loaded"
        assert metric.name == "active_users"
        print("✓ PASSED: Metric persistence")
        passed += 1
        shutil.rmtree(temp_storage.parent)
    except Exception as e:
        print(f"✗ FAILED: Metric persistence - {str(e)}")
        failed += 1

    # Test 3: Invalid model validation
    print("\n[3/15] Testing invalid model validation...")
    try:
        temp_storage = Path(tempfile.mkdtemp()) / "test_metrics.json"
        mock_manager = MockSemanticManager()

        registry = runtime_metrics.RuntimeMetricRegistry(temp_storage)

        result = await registry.define_metric(
            name="test_metric",
            type="count",
            model="nonexistent_model",
            semantic_manager=mock_manager,
        )

        assert result["status"] == "error"
        assert "not found" in result["error"].lower()
        print("✓ PASSED: Invalid model validation")
        passed += 1
        shutil.rmtree(temp_storage.parent)
    except Exception as e:
        print(f"✗ FAILED: Invalid model validation - {str(e)}")
        failed += 1

    # Test 4: Invalid dimension validation
    print("\n[4/15] Testing invalid dimension validation...")
    try:
        temp_storage = Path(tempfile.mkdtemp()) / "test_metrics.json"
        mock_manager = MockSemanticManager()

        registry = runtime_metrics.RuntimeMetricRegistry(temp_storage)

        result = await registry.define_metric(
            name="test_metric",
            type="count_distinct",
            model="users",
            semantic_manager=mock_manager,
            dimension="nonexistent_dimension",
        )

        assert result["status"] == "error"
        assert "dimension" in result["error"].lower()
        print("✓ PASSED: Invalid dimension validation")
        passed += 1
        shutil.rmtree(temp_storage.parent)
    except Exception as e:
        print(f"✗ FAILED: Invalid dimension validation - {str(e)}")
        failed += 1

    # Test 5: Ratio metric creation
    print("\n[5/15] Testing ratio metric creation...")
    try:
        temp_storage = Path(tempfile.mkdtemp()) / "test_metrics.json"
        mock_manager = MockSemanticManager()

        registry = runtime_metrics.RuntimeMetricRegistry(temp_storage)

        result = await registry.define_metric(
            name="conversion_rate",
            type="ratio",
            model="users",
            semantic_manager=mock_manager,
            description="Conversion rate",
            numerator="paid_users",
            denominator="total_users",
        )

        assert result["status"] == "success"
        assert result["metric"]["numerator"] == "paid_users"
        print("✓ PASSED: Ratio metric creation")
        passed += 1
        shutil.rmtree(temp_storage.parent)
    except Exception as e:
        print(f"✗ FAILED: Ratio metric creation - {str(e)}")
        failed += 1

    # Test 6: Ratio validation
    print("\n[6/15] Testing ratio metric validation...")
    try:
        temp_storage = Path(tempfile.mkdtemp()) / "test_metrics.json"
        mock_manager = MockSemanticManager()

        registry = runtime_metrics.RuntimeMetricRegistry(temp_storage)

        result = await registry.define_metric(
            name="incomplete_ratio",
            type="ratio",
            model="users",
            semantic_manager=mock_manager,
            numerator="paid_users",
        )

        assert result["status"] == "error"
        assert "denominator" in result["error"].lower()
        print("✓ PASSED: Ratio metric validation")
        passed += 1
        shutil.rmtree(temp_storage.parent)
    except Exception as e:
        print(f"✗ FAILED: Ratio metric validation - {str(e)}")
        failed += 1

    # Test 7: List metrics
    print("\n[7/15] Testing list metrics...")
    try:
        temp_storage = Path(tempfile.mkdtemp()) / "test_metrics.json"
        mock_manager = MockSemanticManager()

        registry = runtime_metrics.RuntimeMetricRegistry(temp_storage)

        await registry.define_metric(
            name="metric1", type="count", model="users", semantic_manager=mock_manager
        )

        await registry.define_metric(
            name="metric2", type="count", model="events", semantic_manager=mock_manager
        )

        all_metrics = registry.list_metrics()
        assert len(all_metrics) == 2

        user_metrics = registry.list_metrics(model="users")
        assert len(user_metrics) == 1
        print("✓ PASSED: List metrics")
        passed += 1
        shutil.rmtree(temp_storage.parent)
    except Exception as e:
        print(f"✗ FAILED: List metrics - {str(e)}")
        failed += 1

    # Test 8: List by tags
    print("\n[8/15] Testing list metrics by tags...")
    try:
        temp_storage = Path(tempfile.mkdtemp()) / "test_metrics.json"
        mock_manager = MockSemanticManager()

        registry = runtime_metrics.RuntimeMetricRegistry(temp_storage)

        await registry.define_metric(
            name="metric_engagement",
            type="count",
            model="users",
            semantic_manager=mock_manager,
            tags=["engagement", "core"],
        )

        await registry.define_metric(
            name="metric_revenue",
            type="count",
            model="users",
            semantic_manager=mock_manager,
            tags=["revenue", "core"],
        )

        engagement_metrics = registry.list_metrics(tags=["engagement"])
        assert len(engagement_metrics) == 1
        print("✓ PASSED: List metrics by tags")
        passed += 1
        shutil.rmtree(temp_storage.parent)
    except Exception as e:
        print(f"✗ FAILED: List metrics by tags - {str(e)}")
        failed += 1

    # Test 9: Delete metric
    print("\n[9/15] Testing delete metric...")
    try:
        temp_storage = Path(tempfile.mkdtemp()) / "test_metrics.json"
        mock_manager = MockSemanticManager()

        registry = runtime_metrics.RuntimeMetricRegistry(temp_storage)

        await registry.define_metric(
            name="temp_metric", type="count", model="users", semantic_manager=mock_manager
        )

        result = await registry.delete_metric("temp_metric")
        assert result["status"] == "success"
        assert registry.get_metric("temp_metric") is None
        print("✓ PASSED: Delete metric")
        passed += 1
        shutil.rmtree(temp_storage.parent)
    except Exception as e:
        print(f"✗ FAILED: Delete metric - {str(e)}")
        failed += 1

    # Test 10: Delete nonexistent
    print("\n[10/15] Testing delete nonexistent metric...")
    try:
        temp_storage = Path(tempfile.mkdtemp()) / "test_metrics.json"

        registry = runtime_metrics.RuntimeMetricRegistry(temp_storage)

        result = await registry.delete_metric("nonexistent_metric")
        assert result["status"] == "error"
        print("✓ PASSED: Delete nonexistent metric")
        passed += 1
        shutil.rmtree(temp_storage.parent)
    except Exception as e:
        print(f"✗ FAILED: Delete nonexistent metric - {str(e)}")
        failed += 1

    # Test 11: Duplicate name
    print("\n[11/15] Testing duplicate metric name...")
    try:
        temp_storage = Path(tempfile.mkdtemp()) / "test_metrics.json"
        mock_manager = MockSemanticManager()

        registry = runtime_metrics.RuntimeMetricRegistry(temp_storage)

        result1 = await registry.define_metric(
            name="duplicate_test", type="count", model="users", semantic_manager=mock_manager
        )
        assert result1["status"] == "success"

        result2 = await registry.define_metric(
            name="duplicate_test", type="count", model="users", semantic_manager=mock_manager
        )
        assert result2["status"] == "error"
        assert "already exists" in result2["error"].lower()
        print("✓ PASSED: Duplicate metric name")
        passed += 1
        shutil.rmtree(temp_storage.parent)
    except Exception as e:
        print(f"✗ FAILED: Duplicate metric name - {str(e)}")
        failed += 1

    # Test 12: Invalid type
    print("\n[12/15] Testing invalid metric type...")
    try:
        temp_storage = Path(tempfile.mkdtemp()) / "test_metrics.json"
        mock_manager = MockSemanticManager()

        registry = runtime_metrics.RuntimeMetricRegistry(temp_storage)

        result = await registry.define_metric(
            name="invalid_type",
            type="invalid_type",
            model="users",
            semantic_manager=mock_manager,
        )

        assert result["status"] == "error"
        assert "invalid metric type" in result["error"].lower()
        print("✓ PASSED: Invalid metric type")
        passed += 1
        shutil.rmtree(temp_storage.parent)
    except Exception as e:
        print(f"✗ FAILED: Invalid metric type - {str(e)}")
        failed += 1

    # Test 13: Custom SQL
    print("\n[13/15] Testing custom SQL metric...")
    try:
        temp_storage = Path(tempfile.mkdtemp()) / "test_metrics.json"
        mock_manager = MockSemanticManager()

        registry = runtime_metrics.RuntimeMetricRegistry(temp_storage)

        result = await registry.define_metric(
            name="custom_calculation",
            type="custom_sql",
            model="users",
            semantic_manager=mock_manager,
            sql="SUM(revenue) / COUNT(DISTINCT user_id)",
        )

        assert result["status"] == "success"
        assert result["metric"]["sql"] is not None
        print("✓ PASSED: Custom SQL metric")
        passed += 1
        shutil.rmtree(temp_storage.parent)
    except Exception as e:
        print(f"✗ FAILED: Custom SQL metric - {str(e)}")
        failed += 1

    # Test 14: Custom SQL validation
    print("\n[14/15] Testing custom SQL validation...")
    try:
        temp_storage = Path(tempfile.mkdtemp()) / "test_metrics.json"
        mock_manager = MockSemanticManager()

        registry = runtime_metrics.RuntimeMetricRegistry(temp_storage)

        result = await registry.define_metric(
            name="missing_sql",
            type="custom_sql",
            model="users",
            semantic_manager=mock_manager,
        )

        assert result["status"] == "error"
        assert "sql" in result["error"].lower()
        print("✓ PASSED: Custom SQL validation")
        passed += 1
        shutil.rmtree(temp_storage.parent)
    except Exception as e:
        print(f"✗ FAILED: Custom SQL validation - {str(e)}")
        failed += 1

    # Test 15: Metadata
    print("\n[15/15] Testing metric metadata...")
    try:
        temp_storage = Path(tempfile.mkdtemp()) / "test_metrics.json"
        mock_manager = MockSemanticManager()

        registry = runtime_metrics.RuntimeMetricRegistry(temp_storage)

        await registry.define_metric(
            name="metadata_test",
            type="count",
            model="users",
            semantic_manager=mock_manager,
            description="Test metric",
        )

        metric = registry.get_metric("metadata_test")
        assert metric.created_at is not None
        assert metric.created_by == "user"
        print("✓ PASSED: Metric metadata")
        passed += 1
        shutil.rmtree(temp_storage.parent)
    except Exception as e:
        print(f"✗ FAILED: Metric metadata - {str(e)}")
        failed += 1

    # Print results
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed out of 15 tests")
    print("=" * 60 + "\n")

    if failed == 0:
        print("✅ ALL TESTS PASSED!")
        return True
    else:
        print(f"❌ {failed} TEST(S) FAILED")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
