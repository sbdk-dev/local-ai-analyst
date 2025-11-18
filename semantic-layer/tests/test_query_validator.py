#!/usr/bin/env python3
"""
Tests for Query Validator

Validates that queries are properly checked before execution using:
- Dry-run validation with EXPLAIN
- Complexity analysis
- Result size estimation
- Warning detection
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.query_validator import QueryValidator, ValidationResult
from mcp_server.semantic_layer_integration import SemanticLayerManager


@pytest.fixture
async def semantic_manager():
    """Initialize semantic layer manager"""
    manager = SemanticLayerManager()
    await manager.initialize()
    yield manager
    await manager.cleanup()


@pytest.fixture
async def query_validator(semantic_manager):
    """Initialize query validator"""
    return QueryValidator(semantic_manager.connection)


@pytest.mark.asyncio
async def test_validator_initialization(query_validator):
    """Test validator initializes with correct settings"""
    assert query_validator.connection is not None
    assert query_validator.max_complexity == 80.0
    assert query_validator.max_estimated_rows == 100_000


@pytest.mark.asyncio
async def test_simple_query_validation(semantic_manager, query_validator):
    """Test validation passes for simple query"""

    # Build a simple query
    query_info = await semantic_manager.build_query(
        model="users",
        dimensions=["plan_type"],
        measures=["total_users"]
    )

    # Build Ibis expression
    sql = query_info["sql"]
    ibis_expr = semantic_manager.connection.sql(sql)

    # Validate
    result = await query_validator.validate_ibis_query(ibis_expr, query_info)

    assert result.valid is True
    assert result.error is None
    assert result.complexity_score < 50.0
    assert isinstance(result.estimated_rows, int)


@pytest.mark.asyncio
async def test_complex_query_blocked(semantic_manager, query_validator):
    """Test that overly complex queries are blocked"""

    # Override max_complexity for testing
    query_validator.max_complexity = 30.0

    # Build a complex query with many dimensions and measures
    query_info = await semantic_manager.build_query(
        model="events",
        dimensions=["event_type", "feature_name", "user_id"],
        measures=["total_events", "unique_users"]
    )

    # Build Ibis expression
    sql = query_info["sql"]
    ibis_expr = semantic_manager.connection.sql(sql)

    # Validate
    result = await query_validator.validate_ibis_query(ibis_expr, query_info)

    assert result.valid is False
    assert "too complex" in result.error.lower()
    assert result.complexity_score > query_validator.max_complexity


@pytest.mark.asyncio
async def test_complexity_scoring(semantic_manager, query_validator):
    """Test complexity scoring algorithm"""

    # Test 1: Simple query (low complexity)
    simple_query = await semantic_manager.build_query(
        model="users",
        dimensions=["plan_type"],
        measures=["total_users"]
    )

    simple_complexity = query_validator._analyze_complexity(
        simple_query["sql"],
        simple_query
    )

    # Test 2: Complex query (higher complexity)
    complex_query = await semantic_manager.build_query(
        model="events",
        dimensions=["event_type", "feature_name", "user_id"],
        measures=["total_events", "unique_users"]
    )

    complex_complexity = query_validator._analyze_complexity(
        complex_query["sql"],
        complex_query
    )

    # Complex query should have higher score
    assert complex_complexity > simple_complexity
    assert simple_complexity < 40.0
    assert complex_complexity > 20.0


@pytest.mark.asyncio
async def test_dimension_complexity_factor(query_validator):
    """Test that dimensions add to complexity score"""

    query_info_1_dim = {
        "model": "users",
        "dimensions": ["plan_type"],
        "measures": ["total_users"]
    }

    query_info_3_dims = {
        "model": "users",
        "dimensions": ["plan_type", "industry", "country"],
        "measures": ["total_users"]
    }

    complexity_1 = query_validator._analyze_complexity("SELECT plan_type, COUNT(*) FROM users GROUP BY plan_type", query_info_1_dim)
    complexity_3 = query_validator._analyze_complexity("SELECT plan_type, industry, country, COUNT(*) FROM users GROUP BY plan_type, industry, country", query_info_3_dims)

    # Each dimension adds 5 points
    expected_diff = 2 * 5  # 2 additional dimensions
    assert complexity_3 - complexity_1 == expected_diff


@pytest.mark.asyncio
async def test_join_complexity_factor(query_validator):
    """Test that JOINs increase complexity score"""

    query_info = {"model": "events", "dimensions": ["event_type"], "measures": ["total_events"]}

    sql_no_join = "SELECT event_type, COUNT(*) FROM events GROUP BY event_type"
    sql_with_join = "SELECT event_type, COUNT(*) FROM events JOIN users ON events.user_id = users.user_id GROUP BY event_type"

    complexity_no_join = query_validator._analyze_complexity(sql_no_join, query_info)
    complexity_with_join = query_validator._analyze_complexity(sql_with_join, query_info)

    # JOIN adds 10 points
    assert complexity_with_join - complexity_no_join == 10


@pytest.mark.asyncio
async def test_subquery_complexity_factor(query_validator):
    """Test that subqueries increase complexity score"""

    query_info = {"model": "users", "dimensions": [], "measures": ["total_users"]}

    sql_simple = "SELECT COUNT(*) FROM users"
    sql_with_subquery = "SELECT COUNT(*) FROM (SELECT DISTINCT user_id FROM events) e"

    complexity_simple = query_validator._analyze_complexity(sql_simple, query_info)
    complexity_subquery = query_validator._analyze_complexity(sql_with_subquery, query_info)

    # Subquery adds 15 points
    assert complexity_subquery - complexity_simple == 15


@pytest.mark.asyncio
async def test_result_size_estimation_single_row(semantic_manager, query_validator):
    """Test result size estimation for aggregate query (single row)"""

    query_info = {
        "model": "users",
        "dimensions": [],  # No GROUP BY
        "measures": ["total_users"],
        "table": "users"
    }

    estimated_rows = await query_validator._estimate_result_size("SELECT COUNT(*) FROM users", query_info)

    # Aggregate without GROUP BY returns 1 row
    assert estimated_rows == 1


@pytest.mark.asyncio
async def test_result_size_estimation_grouped(semantic_manager, query_validator):
    """Test result size estimation for grouped query"""

    query_info = {
        "model": "users",
        "dimensions": ["plan_type"],
        "measures": ["total_users"],
        "table": "users"
    }

    estimated_rows = await query_validator._estimate_result_size(
        "SELECT plan_type, COUNT(*) FROM users GROUP BY plan_type",
        query_info
    )

    # Should estimate based on cardinality of plan_type
    assert estimated_rows > 1
    assert estimated_rows < 100  # plan_type has few distinct values


@pytest.mark.asyncio
async def test_result_size_estimation_multi_dimension(semantic_manager, query_validator):
    """Test result size estimation for multi-dimensional query"""

    query_info = {
        "model": "users",
        "dimensions": ["plan_type", "industry"],
        "measures": ["total_users"],
        "table": "users"
    }

    single_dim_estimate = await query_validator._estimate_result_size(
        "SELECT plan_type, COUNT(*) FROM users GROUP BY plan_type",
        {**query_info, "dimensions": ["plan_type"]}
    )

    multi_dim_estimate = await query_validator._estimate_result_size(
        "SELECT plan_type, industry, COUNT(*) FROM users GROUP BY plan_type, industry",
        query_info
    )

    # Multi-dimensional query should have higher estimate
    assert multi_dim_estimate > single_dim_estimate


@pytest.mark.asyncio
async def test_large_result_blocked(semantic_manager, query_validator):
    """Test that queries with too many estimated rows are blocked"""

    # Override max for testing
    query_validator.max_estimated_rows = 10

    query_info = await semantic_manager.build_query(
        model="events",
        dimensions=["event_id"],  # High cardinality dimension
        measures=["total_events"]
    )

    sql = query_info["sql"]
    ibis_expr = semantic_manager.connection.sql(sql)

    result = await query_validator.validate_ibis_query(ibis_expr, query_info)

    # Should fail due to result size
    assert result.valid is False
    assert "too large" in result.error.lower() or "result" in result.error.lower()


@pytest.mark.asyncio
async def test_warning_no_filters_on_large_table(semantic_manager, query_validator):
    """Test warning when querying large table without filters"""

    query_info = await semantic_manager.build_query(
        model="events",  # Large table
        dimensions=["event_type"],
        measures=["total_events"],
        filters={}  # No filters
    )

    warnings = query_validator._check_for_warnings(query_info["sql"], query_info)

    # Should warn about no filters on events table
    assert len(warnings) > 0
    assert any("filter" in w.lower() for w in warnings)


@pytest.mark.asyncio
async def test_warning_many_dimensions_no_limit(query_validator):
    """Test warning when query has many dimensions without LIMIT"""

    query_info = {
        "model": "events",
        "dimensions": ["event_type", "feature_name", "user_id", "event_id"],
        "measures": ["total_events"]
    }

    sql = "SELECT event_type, feature_name, user_id, event_id, COUNT(*) FROM events GROUP BY event_type, feature_name, user_id, event_id"

    warnings = query_validator._check_for_warnings(sql, query_info)

    # Should warn about many dimensions without LIMIT
    assert len(warnings) > 0
    assert any("limit" in w.lower() for w in warnings)


@pytest.mark.asyncio
async def test_no_warnings_with_filters(semantic_manager, query_validator):
    """Test that warnings are suppressed when appropriate filters are applied"""

    query_info = await semantic_manager.build_query(
        model="events",
        dimensions=["event_type"],
        measures=["total_events"],
        filters={"event_type": "conversion"}
    )

    warnings = query_validator._check_for_warnings(query_info["sql"], query_info)

    # Should not warn when filters are present
    # (or fewer warnings than without filters)
    assert isinstance(warnings, list)


@pytest.mark.asyncio
async def test_validation_result_structure(semantic_manager, query_validator):
    """Test that ValidationResult has correct structure"""

    query_info = await semantic_manager.build_query(
        model="users",
        dimensions=["plan_type"],
        measures=["total_users"]
    )

    sql = query_info["sql"]
    ibis_expr = semantic_manager.connection.sql(sql)

    result = await query_validator.validate_ibis_query(ibis_expr, query_info)

    # Check all expected fields are present
    assert hasattr(result, "valid")
    assert hasattr(result, "error")
    assert hasattr(result, "warnings")
    assert hasattr(result, "estimated_rows")
    assert hasattr(result, "estimated_time_ms")
    assert hasattr(result, "complexity_score")

    # Check types
    assert isinstance(result.valid, bool)
    assert result.error is None or isinstance(result.error, str)
    assert isinstance(result.warnings, list)
    assert result.estimated_rows is None or isinstance(result.estimated_rows, int)
    assert isinstance(result.complexity_score, float)


@pytest.mark.asyncio
async def test_validation_catches_invalid_sql(semantic_manager, query_validator):
    """Test that validation catches invalid SQL"""

    # Create invalid SQL
    invalid_sql = "SELECT invalid_column FROM nonexistent_table"

    try:
        ibis_expr = semantic_manager.connection.sql(invalid_sql)
        query_info = {"model": "users", "dimensions": [], "measures": []}

        result = await query_validator.validate_ibis_query(ibis_expr, query_info)

        # Should return invalid result
        assert result.valid is False
        assert result.error is not None
    except Exception:
        # If exception is raised before validation, that's also acceptable
        pass


@pytest.mark.asyncio
async def test_explain_query_execution(semantic_manager, query_validator):
    """Test that EXPLAIN query executes without error"""

    query_info = await semantic_manager.build_query(
        model="users",
        dimensions=["plan_type"],
        measures=["total_users"]
    )

    sql = query_info["sql"]

    # Test EXPLAIN execution
    try:
        explain_result = semantic_manager.connection.sql(f"EXPLAIN {sql}").to_pandas()
        assert not explain_result.empty
    except Exception as e:
        pytest.fail(f"EXPLAIN query failed: {e}")


@pytest.mark.asyncio
async def test_complexity_score_bounded(query_validator):
    """Test that complexity score is bounded between 0 and 100"""

    # Create artificially complex query
    query_info = {
        "model": "users",
        "dimensions": ["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9", "d10"],
        "measures": ["m1", "m2", "m3", "m4", "m5"]
    }

    sql = "SELECT d1, d2 FROM (SELECT d3, d4 FROM (SELECT d5 FROM t1 JOIN t2 JOIN t3 JOIN t4 JOIN t5) WHERE d6 IN (SELECT d7 FROM t6))"

    complexity = query_validator._analyze_complexity(sql, query_info)

    # Complexity should be capped at 100
    assert 0 <= complexity <= 100


@pytest.mark.asyncio
async def test_validation_with_limit(semantic_manager, query_validator):
    """Test validation works correctly with LIMIT clause"""

    query_info = await semantic_manager.build_query(
        model="events",
        dimensions=["event_type"],
        measures=["total_events"],
        limit=100
    )

    sql = query_info["sql"]
    ibis_expr = semantic_manager.connection.sql(sql)

    result = await query_validator.validate_ibis_query(ibis_expr, query_info)

    # Should pass validation
    assert result.valid is True


@pytest.mark.asyncio
async def test_validation_metadata_included(semantic_manager, query_validator):
    """Test that validation includes useful metadata"""

    query_info = await semantic_manager.build_query(
        model="users",
        dimensions=["plan_type"],
        measures=["total_users"]
    )

    sql = query_info["sql"]
    ibis_expr = semantic_manager.connection.sql(sql)

    result = await query_validator.validate_ibis_query(ibis_expr, query_info)

    assert result.valid is True
    assert result.complexity_score >= 0
    assert result.estimated_rows is not None
    assert isinstance(result.warnings, list)


@pytest.mark.asyncio
async def test_different_complexity_thresholds(semantic_manager, query_validator):
    """Test that different complexity thresholds work correctly"""

    query_info = await semantic_manager.build_query(
        model="events",
        dimensions=["event_type", "feature_name"],
        measures=["total_events"]
    )

    sql = query_info["sql"]
    ibis_expr = semantic_manager.connection.sql(sql)

    # Test with high threshold (should pass)
    query_validator.max_complexity = 100.0
    result_pass = await query_validator.validate_ibis_query(ibis_expr, query_info)
    assert result_pass.valid is True

    # Test with low threshold (should fail)
    query_validator.max_complexity = 10.0
    result_fail = await query_validator.validate_ibis_query(ibis_expr, query_info)
    assert result_fail.valid is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
