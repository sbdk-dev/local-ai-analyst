#!/usr/bin/env python3
"""
Standalone test for QueryValidator (doesn't import server.py)
"""

import asyncio
import sys
from pathlib import Path

# Import only what we need
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server.query_validator import QueryValidator, ValidationResult
from mcp_server.semantic_layer_integration import SemanticLayerManager


async def main():
    print("=" * 80)
    print("QueryValidator Standalone Tests")
    print("=" * 80)

    # Initialize semantic manager
    print("\n1. Initializing SemanticLayerManager...")
    manager = SemanticLayerManager()
    await manager.initialize()
    print("   ✓ SemanticLayerManager initialized")

    # Initialize validator
    print("\n2. Initializing QueryValidator...")
    validator = QueryValidator(manager.connection)
    print(f"   ✓ QueryValidator initialized (max_complexity={validator.max_complexity}, max_rows={validator.max_estimated_rows:,})")

    # Test 1: Simple query validation
    print("\n3. Test: Simple query validation")
    query_info = await manager.build_query(
        model="users",
        dimensions=["plan_type"],
        measures=["total_users"]
    )

    sql = query_info["sql"]
    ibis_expr = manager.connection.sql(sql)

    result = await validator.validate_ibis_query(ibis_expr, query_info)

    print(f"   Valid: {result.valid}")
    print(f"   Complexity: {result.complexity_score:.1f}")
    print(f"   Estimated rows: {result.estimated_rows}")
    print(f"   Warnings: {len(result.warnings)}")

    if result.valid:
        print("   ✓ Simple query validation PASSED")
    else:
        print(f"   ✗ Simple query validation FAILED: {result.error}")
        return False

    # Test 2: Complexity scoring
    print("\n4. Test: Complexity scoring")
    simple_complexity = validator._analyze_complexity(query_info["sql"], query_info)

    complex_query = await manager.build_query(
        model="events",
        dimensions=["event_type", "feature_name", "user_id"],
        measures=["total_events", "unique_users"]
    )
    complex_complexity = validator._analyze_complexity(complex_query["sql"], complex_query)

    print(f"   Simple query complexity: {simple_complexity:.1f}")
    print(f"   Complex query complexity: {complex_complexity:.1f}")

    if complex_complexity > simple_complexity:
        print("   ✓ Complexity scoring PASSED")
    else:
        print(f"   ✗ Complexity scoring FAILED: complex should be > simple")
        return False

    # Test 3: Result size estimation
    print("\n5. Test: Result size estimation")

    single_row_query = {
        "model": "users",
        "dimensions": [],
        "measures": ["total_users"],
        "table": "users"
    }
    estimated_single = await validator._estimate_result_size("SELECT COUNT(*) FROM users", single_row_query)

    grouped_query = {
        "model": "users",
        "dimensions": ["plan_type"],
        "measures": ["total_users"],
        "table": "users"
    }
    estimated_grouped = await validator._estimate_result_size("SELECT plan_type, COUNT(*) FROM users GROUP BY plan_type", grouped_query)

    print(f"   Single row estimate: {estimated_single}")
    print(f"   Grouped query estimate: {estimated_grouped}")

    if estimated_single == 1 and estimated_grouped > 1:
        print("   ✓ Result size estimation PASSED")
    else:
        print(f"   ✗ Result size estimation FAILED")
        return False

    # Test 4: Warning detection
    print("\n6. Test: Warning detection")

    events_query = await manager.build_query(
        model="events",
        dimensions=["event_type"],
        measures=["total_events"],
        filters={}
    )

    warnings = validator._check_for_warnings(events_query["sql"], events_query)

    print(f"   Warnings found: {len(warnings)}")
    for i, warning in enumerate(warnings, 1):
        print(f"      {i}. {warning}")

    if len(warnings) > 0:
        print("   ✓ Warning detection PASSED")
    else:
        print("   ℹ Warning detection: no warnings (may be OK)")

    # Test 5: Complex query blocking
    print("\n7. Test: Complex query blocking")

    # Temporarily lower threshold
    original_max = validator.max_complexity
    validator.max_complexity = 30.0

    complex_query = await manager.build_query(
        model="events",
        dimensions=["event_type", "feature_name", "user_id"],
        measures=["total_events", "unique_users"]
    )

    complex_expr = manager.connection.sql(complex_query["sql"])
    complex_result = await validator.validate_ibis_query(complex_expr, complex_query)

    # Restore threshold
    validator.max_complexity = original_max

    print(f"   Valid: {complex_result.valid}")
    print(f"   Error: {complex_result.error if not complex_result.valid else 'None'}")

    if not complex_result.valid and "complex" in complex_result.error.lower():
        print("   ✓ Complex query blocking PASSED")
    else:
        print(f"   ✗ Complex query blocking FAILED")
        return False

    # Test 6: EXPLAIN query execution
    print("\n8. Test: EXPLAIN query execution")

    try:
        explain_result = manager.connection.sql(f"EXPLAIN {query_info['sql']}").to_pandas()
        if not explain_result.empty:
            print(f"   EXPLAIN returned {len(explain_result)} rows")
            print("   ✓ EXPLAIN query PASSED")
        else:
            print("   ✗ EXPLAIN query returned empty result")
            return False
    except Exception as e:
        print(f"   ✗ EXPLAIN query FAILED: {e}")
        return False

    # Cleanup
    await manager.cleanup()

    print("\n" + "=" * 80)
    print("ALL TESTS PASSED ✓")
    print("=" * 80)

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
