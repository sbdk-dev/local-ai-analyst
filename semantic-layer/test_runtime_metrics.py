#!/usr/bin/env python3
"""
Tests for Runtime Metrics System

Tests cover:
1. Metric creation and validation
2. Metric persistence and loading
3. Metric deletion
4. Integration with query execution
5. Error handling and edge cases
"""

import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
                "measures": ["total_users", "avg_ltv"]
            },
            {
                "name": "events",
                "description": "Event tracking",
                "table": "events",
                "dimensions": ["event_type", "user_id", "date"],
                "measures": ["total_events", "unique_users"]
            }
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
                    {"name": "signup_date", "type": "date"}
                ],
                "measures": [
                    {"name": "total_users", "type": "count"},
                    {"name": "avg_ltv", "type": "avg"}
                ]
            }
        elif model_name == "events":
            return {
                "name": "events",
                "dimensions": [
                    {"name": "event_type", "type": "string"},
                    {"name": "user_id", "type": "string"},
                    {"name": "date", "type": "date"}
                ],
                "measures": [
                    {"name": "total_events", "type": "count"},
                    {"name": "unique_users", "type": "count_distinct"}
                ]
            }
        else:
            raise ValueError(f"Unknown model: {model_name}")


class TestRuntimeMetrics:
    """Test suite for runtime metrics system"""

    # Test 1: Basic metric creation
    async def test_create_count_metric(self, temp_storage_path, mock_semantic_manager):
        """Test creating a simple count metric"""
        from mcp_server.runtime_metrics import RuntimeMetricRegistry

        registry = RuntimeMetricRegistry(temp_storage_path)

        result = await registry.define_metric(
            name="power_users",
            type="count_distinct",
            model="users",
            semantic_manager=mock_semantic_manager,
            description="Users with 100+ logins",
            dimension="user_id",
            filters={"login_count__gt": 100},
            tags=["engagement", "power_users"]
        )

        assert result["status"] == "success", f"Failed to create metric: {result.get('error')}"
        assert result["metric"]["name"] == "power_users"
        assert result["metric"]["type"] == "count_distinct"
        assert result["metric"]["model"] == "users"
        assert result["metric"]["dimension"] == "user_id"
        assert result["metric"]["filters"]["login_count__gt"] == 100
        assert "engagement" in result["metric"]["tags"]

        logger.info("✓ Test 1 passed: Basic metric creation")

    # Test 2: Metric persistence
    async def test_metric_persistence(self, temp_storage_path, mock_semantic_manager):
        """Test that metrics are persisted and loaded correctly"""
        from mcp_server.runtime_metrics import RuntimeMetricRegistry

        # Create registry and add metric
        registry1 = RuntimeMetricRegistry(temp_storage_path)
        await registry1.define_metric(
            name="active_users",
            type="count_distinct",
            model="users",
            semantic_manager=mock_semantic_manager,
            dimension="user_id",
            filters={"last_login__gte": "2024-01-01"}
        )

        # Create new registry instance (simulates restart)
        registry2 = RuntimeMetricRegistry(temp_storage_path)

        # Check that metric was loaded
        metric = registry2.get_metric("active_users")
        assert metric is not None, "Metric not loaded from storage"
        assert metric.name == "active_users"
        assert metric.type == "count_distinct"
        assert metric.dimension == "user_id"

        logger.info("✓ Test 2 passed: Metric persistence")

    # Test 3: Metric validation - invalid model
    async def test_invalid_model_validation(self, temp_storage_path, mock_semantic_manager):
        """Test that invalid model names are rejected"""
        from mcp_server.runtime_metrics import RuntimeMetricRegistry

        registry = RuntimeMetricRegistry(temp_storage_path)

        result = await registry.define_metric(
            name="test_metric",
            type="count",
            model="nonexistent_model",
            semantic_manager=mock_semantic_manager
        )

        assert result["status"] == "error"
        assert "not found" in result["error"].lower()

        logger.info("✓ Test 3 passed: Invalid model validation")

    # Test 4: Metric validation - invalid dimension
    async def test_invalid_dimension_validation(self, temp_storage_path, mock_semantic_manager):
        """Test that invalid dimension names are rejected"""
        from mcp_server.runtime_metrics import RuntimeMetricRegistry

        registry = RuntimeMetricRegistry(temp_storage_path)

        result = await registry.define_metric(
            name="test_metric",
            type="count_distinct",
            model="users",
            semantic_manager=mock_semantic_manager,
            dimension="nonexistent_dimension"
        )

        assert result["status"] == "error"
        assert "dimension" in result["error"].lower()

        logger.info("✓ Test 4 passed: Invalid dimension validation")

    # Test 5: Ratio metric creation
    async def test_create_ratio_metric(self, temp_storage_path, mock_semantic_manager):
        """Test creating a ratio metric"""
        from mcp_server.runtime_metrics import RuntimeMetricRegistry

        registry = RuntimeMetricRegistry(temp_storage_path)

        result = await registry.define_metric(
            name="conversion_rate",
            type="ratio",
            model="users",
            semantic_manager=mock_semantic_manager,
            description="Conversion rate from free to paid",
            numerator="paid_users",
            denominator="total_users"
        )

        assert result["status"] == "success"
        assert result["metric"]["type"] == "ratio"
        assert result["metric"]["numerator"] == "paid_users"
        assert result["metric"]["denominator"] == "total_users"

        logger.info("✓ Test 5 passed: Ratio metric creation")

    # Test 6: Ratio metric validation
    async def test_ratio_metric_missing_components(self, temp_storage_path, mock_semantic_manager):
        """Test that ratio metrics require numerator and denominator"""
        from mcp_server.runtime_metrics import RuntimeMetricRegistry

        registry = RuntimeMetricRegistry(temp_storage_path)

        # Missing denominator
        result = await registry.define_metric(
            name="incomplete_ratio",
            type="ratio",
            model="users",
            semantic_manager=mock_semantic_manager,
            numerator="paid_users"
        )

        assert result["status"] == "error"
        assert "denominator" in result["error"].lower()

        logger.info("✓ Test 6 passed: Ratio metric validation")

    # Test 7: List metrics
    async def test_list_metrics(self, temp_storage_path, mock_semantic_manager):
        """Test listing all metrics"""
        from mcp_server.runtime_metrics import RuntimeMetricRegistry

        registry = RuntimeMetricRegistry(temp_storage_path)

        # Create multiple metrics
        await registry.define_metric(
            name="metric1",
            type="count",
            model="users",
            semantic_manager=mock_semantic_manager
        )

        await registry.define_metric(
            name="metric2",
            type="count",
            model="events",
            semantic_manager=mock_semantic_manager
        )

        # List all metrics
        all_metrics = registry.list_metrics()
        assert len(all_metrics) == 2

        # List metrics for specific model
        user_metrics = registry.list_metrics(model="users")
        assert len(user_metrics) == 1
        assert user_metrics[0].name == "metric1"

        logger.info("✓ Test 7 passed: List metrics")

    # Test 8: List metrics by tags
    async def test_list_metrics_by_tags(self, temp_storage_path, mock_semantic_manager):
        """Test filtering metrics by tags"""
        from mcp_server.runtime_metrics import RuntimeMetricRegistry

        registry = RuntimeMetricRegistry(temp_storage_path)

        # Create metrics with different tags
        await registry.define_metric(
            name="metric_engagement",
            type="count",
            model="users",
            semantic_manager=mock_semantic_manager,
            tags=["engagement", "core"]
        )

        await registry.define_metric(
            name="metric_revenue",
            type="sum",
            model="users",
            semantic_manager=mock_semantic_manager,
            dimension="revenue",
            tags=["revenue", "core"]
        )

        # Filter by tag
        engagement_metrics = registry.list_metrics(tags=["engagement"])
        assert len(engagement_metrics) == 1
        assert engagement_metrics[0].name == "metric_engagement"

        core_metrics = registry.list_metrics(tags=["core"])
        assert len(core_metrics) == 2

        logger.info("✓ Test 8 passed: List metrics by tags")

    # Test 9: Delete metric
    async def test_delete_metric(self, temp_storage_path, mock_semantic_manager):
        """Test deleting a metric"""
        from mcp_server.runtime_metrics import RuntimeMetricRegistry

        registry = RuntimeMetricRegistry(temp_storage_path)

        # Create metric
        await registry.define_metric(
            name="temp_metric",
            type="count",
            model="users",
            semantic_manager=mock_semantic_manager
        )

        # Verify it exists
        assert registry.get_metric("temp_metric") is not None

        # Delete it
        result = await registry.delete_metric("temp_metric")
        assert result["status"] == "success"

        # Verify it's gone
        assert registry.get_metric("temp_metric") is None

        logger.info("✓ Test 9 passed: Delete metric")

    # Test 10: Delete nonexistent metric
    async def test_delete_nonexistent_metric(self, temp_storage_path, mock_semantic_manager):
        """Test deleting a metric that doesn't exist"""
        from mcp_server.runtime_metrics import RuntimeMetricRegistry

        registry = RuntimeMetricRegistry(temp_storage_path)

        result = await registry.delete_metric("nonexistent_metric")
        assert result["status"] == "error"
        assert "not found" in result["error"].lower()

        logger.info("✓ Test 10 passed: Delete nonexistent metric")

    # Test 11: Duplicate metric name
    async def test_duplicate_metric_name(self, temp_storage_path, mock_semantic_manager):
        """Test that duplicate metric names are rejected"""
        from mcp_server.runtime_metrics import RuntimeMetricRegistry

        registry = RuntimeMetricRegistry(temp_storage_path)

        # Create first metric
        result1 = await registry.define_metric(
            name="duplicate_test",
            type="count",
            model="users",
            semantic_manager=mock_semantic_manager
        )
        assert result1["status"] == "success"

        # Try to create duplicate
        result2 = await registry.define_metric(
            name="duplicate_test",
            type="count",
            model="users",
            semantic_manager=mock_semantic_manager
        )
        assert result2["status"] == "error"
        assert "already exists" in result2["error"].lower()

        logger.info("✓ Test 11 passed: Duplicate metric name rejection")

    # Test 12: Invalid metric type
    async def test_invalid_metric_type(self, temp_storage_path, mock_semantic_manager):
        """Test that invalid metric types are rejected"""
        from mcp_server.runtime_metrics import RuntimeMetricRegistry

        registry = RuntimeMetricRegistry(temp_storage_path)

        result = await registry.define_metric(
            name="invalid_type_metric",
            type="invalid_type",
            model="users",
            semantic_manager=mock_semantic_manager
        )

        assert result["status"] == "error"
        assert "invalid metric type" in result["error"].lower()

        logger.info("✓ Test 12 passed: Invalid metric type rejection")

    # Test 13: Custom SQL metric
    async def test_custom_sql_metric(self, temp_storage_path, mock_semantic_manager):
        """Test creating a custom SQL metric"""
        from mcp_server.runtime_metrics import RuntimeMetricRegistry

        registry = RuntimeMetricRegistry(temp_storage_path)

        result = await registry.define_metric(
            name="custom_calculation",
            type="custom_sql",
            model="users",
            semantic_manager=mock_semantic_manager,
            sql="SUM(revenue) / COUNT(DISTINCT user_id)",
            description="Average revenue per user"
        )

        assert result["status"] == "success"
        assert result["metric"]["type"] == "custom_sql"
        assert result["metric"]["sql"] == "SUM(revenue) / COUNT(DISTINCT user_id)"

        logger.info("✓ Test 13 passed: Custom SQL metric creation")

    # Test 14: Custom SQL validation
    async def test_custom_sql_validation(self, temp_storage_path, mock_semantic_manager):
        """Test that custom SQL metrics require SQL parameter"""
        from mcp_server.runtime_metrics import RuntimeMetricRegistry

        registry = RuntimeMetricRegistry(temp_storage_path)

        result = await registry.define_metric(
            name="missing_sql",
            type="custom_sql",
            model="users",
            semantic_manager=mock_semantic_manager
        )

        assert result["status"] == "error"
        assert "sql" in result["error"].lower()

        logger.info("✓ Test 14 passed: Custom SQL validation")

    # Test 15: Metric metadata
    async def test_metric_metadata(self, temp_storage_path, mock_semantic_manager):
        """Test that metric metadata is properly stored"""
        from mcp_server.runtime_metrics import RuntimeMetricRegistry

        registry = RuntimeMetricRegistry(temp_storage_path)

        result = await registry.define_metric(
            name="metadata_test",
            type="count",
            model="users",
            semantic_manager=mock_semantic_manager,
            description="Test metric with metadata"
        )

        metric = registry.get_metric("metadata_test")

        # Check metadata
        assert metric.created_at is not None
        assert metric.created_by == "user"
        assert isinstance(metric.tags, list)
        assert isinstance(metric.filters, dict)

        logger.info("✓ Test 15 passed: Metric metadata")


async def run_all_tests():
    """Run all runtime metrics tests"""

    print("\n" + "="*60)
    print("RUNTIME METRICS TEST SUITE")
    print("="*60 + "\n")

    test_suite = TestRuntimeMetrics()

    # Create temporary storage for tests
    temp_dir = tempfile.mkdtemp()
    storage_path = Path(temp_dir) / "runtime_metrics.json"
    mock_manager = MockSemanticManager()

    try:
        # Run all tests
        tests = [
            ("Basic metric creation", test_suite.test_create_count_metric),
            ("Metric persistence", test_suite.test_metric_persistence),
            ("Invalid model validation", test_suite.test_invalid_model_validation),
            ("Invalid dimension validation", test_suite.test_invalid_dimension_validation),
            ("Ratio metric creation", test_suite.test_create_ratio_metric),
            ("Ratio metric validation", test_suite.test_ratio_metric_missing_components),
            ("List metrics", test_suite.test_list_metrics),
            ("List metrics by tags", test_suite.test_list_metrics_by_tags),
            ("Delete metric", test_suite.test_delete_metric),
            ("Delete nonexistent metric", test_suite.test_delete_nonexistent_metric),
            ("Duplicate metric name", test_suite.test_duplicate_metric_name),
            ("Invalid metric type", test_suite.test_invalid_metric_type),
            ("Custom SQL metric", test_suite.test_custom_sql_metric),
            ("Custom SQL validation", test_suite.test_custom_sql_validation),
            ("Metric metadata", test_suite.test_metric_metadata),
        ]

        passed = 0
        failed = 0

        for test_name, test_func in tests:
            # Create fresh temp storage for each test
            temp_storage = Path(tempfile.mkdtemp()) / "test_metrics.json"

            try:
                print(f"\nRunning: {test_name}...")
                await test_func(temp_storage, mock_manager)
                passed += 1
                print(f"✓ PASSED: {test_name}")
            except Exception as e:
                failed += 1
                print(f"✗ FAILED: {test_name}")
                print(f"  Error: {str(e)}")
                import traceback
                traceback.print_exc()
            finally:
                # Cleanup temp storage
                if temp_storage.parent.exists():
                    shutil.rmtree(temp_storage.parent)

        print("\n" + "="*60)
        print(f"TEST RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
        print("="*60 + "\n")

        if failed == 0:
            print("✅ ALL TESTS PASSED!")
            return True
        else:
            print(f"❌ {failed} TEST(S) FAILED")
            return False

    finally:
        # Cleanup
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
