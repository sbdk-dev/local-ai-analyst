#!/usr/bin/env python3
"""
Comprehensive Phase 5 Integration Tests

Tests all Phase 5 components working together:
1. SQL Validation Layer
2. RAG Model Discovery
3. Runtime Metrics

Also tests:
- End-to-end analytical workflows
- Performance benchmarks
- MCP tool integration
- No regressions from Phase 4
"""

import asyncio
import time
import tempfile
import shutil
from pathlib import Path
import pytest
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestPhase5Integration:
    """Comprehensive Phase 5 integration tests"""

    @pytest.fixture
    async def semantic_manager(self):
        """Initialize semantic layer manager"""
        from mcp_server.semantic_layer_integration import SemanticLayerManager

        manager = SemanticLayerManager()
        await manager.initialize()
        yield manager
        await manager.cleanup()

    @pytest.fixture
    async def query_validator(self, semantic_manager):
        """Initialize query validator"""
        from mcp_server.query_validator import QueryValidator

        return QueryValidator(semantic_manager.connection)

    @pytest.fixture
    def model_discovery(self):
        """Initialize model discovery"""
        from mcp_server.model_discovery import ModelDiscovery

        models_path = Path(__file__).parent / "models"
        return ModelDiscovery(models_path)

    @pytest.fixture
    async def runtime_metrics(self, semantic_manager):
        """Initialize runtime metrics registry"""
        from mcp_server.runtime_metrics import RuntimeMetricRegistry

        temp_dir = tempfile.mkdtemp()
        storage_path = Path(temp_dir) / "runtime_metrics.json"

        registry = RuntimeMetricRegistry(storage_path)
        yield (registry, semantic_manager)

        # Cleanup
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir)

    # ========================================================================
    # Phase 5.1: SQL Validation Integration Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_validation_integrated_with_query_execution(
        self, semantic_manager, query_validator
    ):
        """Test that validation works seamlessly with query execution"""

        # Build query
        query_info = await semantic_manager.build_query(
            model="users",
            dimensions=["plan_type"],
            measures=["total_users"]
        )

        # Validate
        sql = query_info["sql"]
        ibis_expr = semantic_manager.connection.sql(sql)
        validation_result = await query_validator.validate_ibis_query(ibis_expr, query_info)

        # Should pass validation
        assert validation_result.valid is True
        assert validation_result.complexity_score < 50.0

        # Execute query (only if validation passed)
        if validation_result.valid:
            result = await semantic_manager.execute_query(
                model="users",
                dimensions=["plan_type"],
                measures=["total_users"]
            )

            assert result["status"] == "success"
            assert len(result["results"]) > 0

        logger.info("✓ SQL validation integrated with query execution")

    @pytest.mark.asyncio
    async def test_validation_prevents_bad_queries(
        self, semantic_manager, query_validator
    ):
        """Test that validation catches problems before execution"""

        # Create an overly complex query
        query_validator.max_complexity = 20.0  # Very low threshold

        query_info = await semantic_manager.build_query(
            model="events",
            dimensions=["event_type", "feature_name", "user_id"],
            measures=["total_events", "unique_users"]
        )

        sql = query_info["sql"]
        ibis_expr = semantic_manager.connection.sql(sql)

        validation_result = await query_validator.validate_ibis_query(ibis_expr, query_info)

        # Should fail validation
        assert validation_result.valid is False
        assert "too complex" in validation_result.error.lower()

        logger.info("✓ SQL validation prevents bad queries")

    # ========================================================================
    # Phase 5.2: RAG Model Discovery Integration Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_discovery_integrated_with_query_building(
        self, model_discovery, semantic_manager
    ):
        """Test RAG discovery → query building workflow"""

        # Step 1: User asks question
        question = "What's our revenue by plan type?"

        # Step 2: Discover relevant model
        discovered = await model_discovery.discover_models(question, top_k=1)

        assert len(discovered) > 0
        top_model = discovered[0]["model"]

        # Step 3: Build query on discovered model
        query_result = await semantic_manager.execute_query(
            model=top_model,
            dimensions=["plan_type"],
            measures=["total_revenue"]
        )

        assert query_result["status"] == "success"

        logger.info(f"✓ RAG discovery → query building: {question} → {top_model}")

    @pytest.mark.asyncio
    async def test_discovery_accuracy_on_key_questions(self, model_discovery):
        """Test discovery accuracy on important question types"""

        test_cases = [
            ("How many users do we have?", "users"),
            ("What features are most popular?", "events"),
            ("Show me daily active users", "engagement"),
        ]

        passed = 0
        for question, expected_model in test_cases:
            results = await model_discovery.discover_models(question, top_k=1)

            if results and results[0]["model"] == expected_model:
                passed += 1
                logger.info(f"✓ Discovery correct: '{question}' → {expected_model}")
            else:
                actual_model = results[0]["model"] if results else "none"
                logger.warning(
                    f"✗ Discovery incorrect: '{question}' → {actual_model} (expected: {expected_model})"
                )

        # Should get at least 2/3 correct
        accuracy = passed / len(test_cases)
        assert accuracy >= 0.66, f"Discovery accuracy {accuracy:.1%} below 66% threshold"

        logger.info(f"✓ Discovery accuracy: {passed}/{len(test_cases)} = {accuracy:.1%}")

    @pytest.mark.asyncio
    async def test_discovery_performance(self, model_discovery):
        """Test that discovery meets <100ms performance target"""

        questions = [
            "What's our revenue?",
            "Show me user churn",
            "Feature adoption rates"
        ]

        timings = []

        for question in questions:
            start = time.perf_counter()
            results = await model_discovery.discover_models(question, top_k=3)
            elapsed_ms = (time.perf_counter() - start) * 1000

            timings.append(elapsed_ms)
            assert len(results) > 0, f"No results for: {question}"

        avg_time = sum(timings) / len(timings)
        max_time = max(timings)

        logger.info(f"✓ Discovery performance: avg={avg_time:.1f}ms, max={max_time:.1f}ms")

        # Average should be under 100ms
        assert avg_time < 100, f"Average discovery time {avg_time:.1f}ms exceeds 100ms"

    # ========================================================================
    # Phase 5.3: Runtime Metrics Integration Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_runtime_metric_creation_and_usage(self, runtime_metrics):
        """Test creating custom metric and using it in query"""

        registry, semantic_manager = runtime_metrics

        # Step 1: Create custom metric
        result = await registry.define_metric(
            name="enterprise_users",
            type="count_distinct",
            model="users",
            semantic_manager=semantic_manager,
            description="Count of enterprise plan users",
            dimension="user_id",
            filters={"plan_type": "Enterprise"}
        )

        assert result["status"] == "success"
        assert result["metric"]["name"] == "enterprise_users"

        # Step 2: Verify metric is persisted
        metric = registry.get_metric("enterprise_users")
        assert metric is not None
        assert metric.type == "count_distinct"
        assert metric.filters["plan_type"] == "Enterprise"

        logger.info("✓ Runtime metric created and persisted")

    @pytest.mark.asyncio
    async def test_runtime_metric_validation(self, runtime_metrics):
        """Test that invalid metrics are rejected"""

        registry, semantic_manager = runtime_metrics

        # Test 1: Invalid model
        result = await registry.define_metric(
            name="invalid_metric",
            type="count",
            model="nonexistent_model",
            semantic_manager=semantic_manager
        )

        assert result["status"] == "error"
        assert "not found" in result["error"].lower()

        # Test 2: Invalid dimension
        result = await registry.define_metric(
            name="invalid_dimension",
            type="count_distinct",
            model="users",
            semantic_manager=semantic_manager,
            dimension="nonexistent_dimension"
        )

        assert result["status"] == "error"
        assert "dimension" in result["error"].lower()

        logger.info("✓ Runtime metric validation works")

    @pytest.mark.asyncio
    async def test_runtime_metric_persistence_across_restarts(self, semantic_manager):
        """Test metrics persist across registry restarts"""

        from mcp_server.runtime_metrics import RuntimeMetricRegistry

        temp_dir = tempfile.mkdtemp()
        storage_path = Path(temp_dir) / "test_metrics.json"

        try:
            # Create registry and add metric
            registry1 = RuntimeMetricRegistry(storage_path)
            result = await registry1.define_metric(
                name="persisted_metric",
                type="count",
                model="users",
                semantic_manager=semantic_manager,
                description="Test persistence"
            )

            assert result["status"] == "success"

            # Create new registry (simulates restart)
            registry2 = RuntimeMetricRegistry(storage_path)

            # Verify metric was loaded
            metric = registry2.get_metric("persisted_metric")
            assert metric is not None
            assert metric.name == "persisted_metric"
            assert metric.description == "Test persistence"

            logger.info("✓ Runtime metrics persist across restarts")

        finally:
            if Path(temp_dir).exists():
                shutil.rmtree(temp_dir)

    # ========================================================================
    # End-to-End Integration Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_full_analytical_workflow(
        self, model_discovery, semantic_manager, query_validator
    ):
        """Test complete workflow: discovery → validation → execution"""

        # User asks question
        question = "What's our conversion rate by industry?"

        # Step 1: Discover model
        discovered = await model_discovery.discover_models(question, top_k=1)
        assert len(discovered) > 0
        model_name = discovered[0]["model"]

        # Step 2: Build query
        query_info = await semantic_manager.build_query(
            model=model_name,
            dimensions=["industry"],
            measures=["conversion_rate"]
        )

        # Step 3: Validate query
        sql = query_info["sql"]
        ibis_expr = semantic_manager.connection.sql(sql)
        validation = await query_validator.validate_ibis_query(ibis_expr, query_info)

        assert validation.valid is True

        # Step 4: Execute query
        result = await semantic_manager.execute_query(
            model=model_name,
            dimensions=["industry"],
            measures=["conversion_rate"]
        )

        assert result["status"] == "success"
        assert len(result["results"]) > 0

        logger.info(
            f"✓ Full workflow: {question} → {model_name} → "
            f"{len(result['results'])} results"
        )

    @pytest.mark.asyncio
    async def test_phase_5_components_work_together(
        self, model_discovery, semantic_manager, query_validator, runtime_metrics
    ):
        """Test all Phase 5 components in single workflow"""

        registry, _ = runtime_metrics

        # Step 1: Create custom metric
        metric_result = await registry.define_metric(
            name="power_users",
            type="count_distinct",
            model="users",
            semantic_manager=semantic_manager,
            dimension="user_id",
            description="Users with high engagement"
        )

        assert metric_result["status"] == "success"

        # Step 2: Discover model for question
        question = "How many power users do we have by plan?"
        discovered = await model_discovery.discover_models(question, top_k=1)
        model_name = discovered[0]["model"]

        # Step 3: Build and validate query
        query_info = await semantic_manager.build_query(
            model=model_name,
            dimensions=["plan_type"],
            measures=["total_users"]  # Would use custom metric if integrated
        )

        sql = query_info["sql"]
        ibis_expr = semantic_manager.connection.sql(sql)
        validation = await query_validator.validate_ibis_query(ibis_expr, query_info)

        assert validation.valid is True

        # Step 4: Execute
        result = await semantic_manager.execute_query(
            model=model_name,
            dimensions=["plan_type"],
            measures=["total_users"]
        )

        assert result["status"] == "success"

        logger.info("✓ All Phase 5 components work together")

    # ========================================================================
    # Performance and Regression Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_no_performance_regression(self, semantic_manager):
        """Test that Phase 5 doesn't slow down existing queries"""

        # Baseline: simple query should be fast
        start = time.perf_counter()

        result = await semantic_manager.execute_query(
            model="users",
            dimensions=["plan_type"],
            measures=["total_users"]
        )

        elapsed_ms = (time.perf_counter() - start) * 1000

        assert result["status"] == "success"

        # Should complete in under 500ms (generous threshold)
        assert elapsed_ms < 500, f"Query took {elapsed_ms:.1f}ms (threshold: 500ms)"

        logger.info(f"✓ No performance regression: {elapsed_ms:.1f}ms")

    @pytest.mark.asyncio
    async def test_phase_4_features_still_work(self, semantic_manager):
        """Test that Phase 4 features are not broken by Phase 5"""

        from mcp_server.conversation_memory import ConversationMemory
        from mcp_server.query_optimizer import QueryOptimizer
        from mcp_server.workflow_orchestrator import WorkflowOrchestrator

        # Test conversation memory
        memory = ConversationMemory()
        memory.add_interaction(
            user_input="Test question",
            system_response="Test response",
            context={"test": "data"}
        )

        recent = memory.get_recent_context(limit=1)
        assert len(recent) > 0

        # Test query optimizer
        optimizer = QueryOptimizer()
        await optimizer.start()

        # Test workflow orchestrator
        orchestrator = WorkflowOrchestrator()
        templates = orchestrator.list_available_templates()
        assert len(templates) == 3  # Should have 3 built-in templates

        logger.info("✓ Phase 4 features still work")


async def run_all_tests():
    """Run all Phase 5 integration tests"""

    print("\n" + "="*70)
    print("PHASE 5 INTEGRATION TEST SUITE")
    print("="*70 + "\n")

    # Run with pytest
    import sys
    pytest_args = [
        __file__,
        "-v",
        "-s",
        "--tb=short",
        "-k", "test_"
    ]

    exit_code = pytest.main(pytest_args)

    if exit_code == 0:
        print("\n" + "="*70)
        print("✅ ALL PHASE 5 INTEGRATION TESTS PASSED")
        print("="*70 + "\n")
    else:
        print("\n" + "="*70)
        print("❌ SOME PHASE 5 INTEGRATION TESTS FAILED")
        print("="*70 + "\n")

    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    exit(exit_code)
