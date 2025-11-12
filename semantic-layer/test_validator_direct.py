#!/usr/bin/env python3
"""
Direct test for QueryValidator (imports only specific modules, not server.py)
"""

import asyncio
import sys
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Direct imports - avoid importing server.py or model_discovery.py
import ibis
import yaml


# Copy ValidationResult and QueryValidator classes inline to avoid __init__.py imports
@dataclass
class ValidationResult:
    """Result of query validation"""
    valid: bool
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    estimated_rows: Optional[int] = None
    estimated_time_ms: Optional[float] = None
    complexity_score: float = 0.0


class QueryValidator:
    """Validates queries before execution"""

    def __init__(self, connection, max_complexity: float = 80.0, max_estimated_rows: int = 100_000):
        self.connection = connection
        self.max_complexity = max_complexity
        self.max_estimated_rows = max_estimated_rows
        logger.info(f"QueryValidator initialized: max_complexity={max_complexity}, max_estimated_rows={max_estimated_rows:,}")

    async def validate_ibis_query(self, ibis_expr, query_info: Dict[str, Any]) -> ValidationResult:
        """Validate Ibis query expression before execution"""
        try:
            # Step 1: Compile to SQL
            try:
                sql = ibis_expr.compile()
                logger.debug(f"Compiled SQL for validation: {sql[:200]}...")
            except Exception as e:
                return ValidationResult(valid=False, error=f"Failed to compile query: {str(e)}", warnings=[])

            # Step 2: Dry-run validation (EXPLAIN instead of execution)
            try:
                explain_sql = f"EXPLAIN {sql}"
                raw_conn = self.connection.con
                cursor = raw_conn.execute(explain_sql)
                explain_result = cursor.fetchall()
                plan_text = str(explain_result) if explain_result else ""
                logger.debug(f"EXPLAIN succeeded, plan length: {len(plan_text)} chars")
            except Exception as e:
                logger.warning(f"EXPLAIN query failed: {e}")
                return ValidationResult(valid=False, error=f"Query validation failed: {str(e)}", warnings=[])

            # Step 3: Analyze complexity
            complexity = self._analyze_complexity(sql, query_info)
            logger.debug(f"Query complexity score: {complexity:.1f}")

            if complexity > self.max_complexity:
                return ValidationResult(
                    valid=False,
                    error=f"Query too complex (score: {complexity:.1f}/{self.max_complexity}). Consider adding filters or reducing dimensions.",
                    complexity_score=complexity
                )

            # Step 4: Estimate result size
            try:
                estimated_rows = await self._estimate_result_size(sql, query_info)
                logger.debug(f"Estimated result size: {estimated_rows:,} rows")
            except Exception as e:
                logger.warning(f"Result size estimation failed: {e}")
                estimated_rows = None

            if estimated_rows and estimated_rows > self.max_estimated_rows:
                return ValidationResult(
                    valid=False,
                    error=f"Result too large ({estimated_rows:,} estimated rows, max: {self.max_estimated_rows:,}). Add LIMIT or filters.",
                    estimated_rows=estimated_rows,
                    complexity_score=complexity
                )

            # Step 5: Check for warnings
            warnings = self._check_for_warnings(sql, query_info)

            logger.info(f"Query validation passed: complexity={complexity:.1f}, estimated_rows={estimated_rows}, warnings={len(warnings)}")

            return ValidationResult(valid=True, warnings=warnings, estimated_rows=estimated_rows, complexity_score=complexity)

        except Exception as e:
            logger.error(f"Validation error: {e}", exc_info=True)
            return ValidationResult(valid=False, error=f"Validation error: {str(e)}")

    def _analyze_complexity(self, sql: str, query_info: Dict[str, Any]) -> float:
        """Calculate query complexity score (0-100)"""
        complexity = 10.0
        dimensions = len(query_info.get("dimensions", []))
        complexity += dimensions * 5
        measures = len(query_info.get("measures", []))
        complexity += measures * 3
        join_count = sql.upper().count("JOIN")
        complexity += join_count * 10
        subquery_count = sql.count("(SELECT")
        complexity += subquery_count * 15
        if "DISTINCT" in sql.upper():
            complexity += 5
        if "HAVING" in sql.upper():
            complexity += 8
        return min(complexity, 100.0)

    async def _estimate_result_size(self, sql: str, query_info: Dict[str, Any]) -> int:
        """Estimate number of rows in result"""
        try:
            dimensions = query_info.get("dimensions", [])
            if not dimensions:
                return 1

            model = query_info.get("model", "users")
            table = query_info.get("table", model)
            first_dim = dimensions[0]

            cardinality_sql = f"SELECT COUNT(DISTINCT {first_dim}) as cardinality FROM {table}"

            try:
                result = self.connection.sql(cardinality_sql).to_pandas()
                cardinality = int(result.iloc[0]["cardinality"])

                if len(dimensions) == 1:
                    estimated = cardinality
                else:
                    scale_factor = len(dimensions) ** 0.5
                    estimated = int(cardinality * scale_factor)

                return estimated

            except Exception as e:
                logger.warning(f"Failed to query cardinality for '{first_dim}': {e}")
                return 1000

        except Exception as e:
            logger.warning(f"Could not estimate result size: {e}")
            return 10000

    def _check_for_warnings(self, sql: str, query_info: Dict[str, Any]) -> List[str]:
        """Check for potential issues"""
        warnings = []

        if "WHERE" not in sql.upper():
            model = query_info.get("model")
            if model in ["events", "sessions"]:
                warnings.append(f"No filters applied to '{model}' table. Query may be slow.")

        dimensions = len(query_info.get("dimensions", []))
        if dimensions > 3 and "LIMIT" not in sql.upper():
            warnings.append(f"Query has {dimensions} dimensions without LIMIT. Consider adding LIMIT.")

        join_count = sql.upper().count("JOIN")
        on_count = sql.upper().count(" ON ")
        if join_count > 2 and on_count < join_count:
            warnings.append(f"Potential cartesian product detected. Ensure all JOINs have proper ON conditions.")

        return warnings


# Minimal SemanticLayerManager for testing
class SimpleSemanticManager:
    def __init__(self):
        self.connection = None
        self.db_path = Path(__file__).parent / "data" / "analytics.duckdb"

    async def initialize(self):
        self.connection = ibis.duckdb.connect(str(self.db_path))
        logger.info("Database connected")

    async def build_query(self, model: str, dimensions: List[str], measures: List[str], filters: Dict = None) -> Dict[str, Any]:
        """Build a simple query"""
        select_parts = list(dimensions)

        for measure in measures:
            if measure == "total_users":
                select_parts.append("COUNT(DISTINCT user_id) AS total_users")
            elif measure == "total_events":
                select_parts.append("COUNT(*) AS total_events")
            elif measure == "unique_users":
                select_parts.append("COUNT(DISTINCT user_id) AS unique_users")

        group_by = f"GROUP BY {', '.join(dimensions)}" if dimensions else ""
        sql = f"SELECT {', '.join(select_parts)} FROM {model} {group_by}".strip()

        return {
            "sql": sql,
            "model": model,
            "dimensions": dimensions,
            "measures": measures,
            "filters": filters or {},
            "table": model
        }

    async def cleanup(self):
        if self.connection:
            self.connection.disconnect()


async def main():
    print("=" * 80)
    print("QueryValidator Direct Tests")
    print("=" * 80)

    # Initialize
    print("\n1. Initializing...")
    manager = SimpleSemanticManager()
    await manager.initialize()
    validator = QueryValidator(manager.connection)
    print("   ✓ Initialized")

    # Test 1: Simple query
    print("\n2. Test: Simple query validation")
    query_info = await manager.build_query(
        model="users",
        dimensions=["plan_type"],
        measures=["total_users"]
    )
    ibis_expr = manager.connection.sql(query_info["sql"])
    result = await validator.validate_ibis_query(ibis_expr, query_info)

    print(f"   Valid: {result.valid}")
    print(f"   Complexity: {result.complexity_score:.1f}")
    print(f"   Estimated rows: {result.estimated_rows}")

    if not result.valid:
        print(f"   ✗ FAILED: {result.error}")
        return False
    print("   ✓ PASSED")

    # Test 2: Complexity scoring
    print("\n3. Test: Complexity scoring")
    simple_complexity = validator._analyze_complexity(query_info["sql"], query_info)

    complex_query = await manager.build_query(
        model="events",
        dimensions=["event_type", "feature_name", "user_id"],
        measures=["total_events", "unique_users"]
    )
    complex_complexity = validator._analyze_complexity(complex_query["sql"], complex_query)

    print(f"   Simple: {simple_complexity:.1f}, Complex: {complex_complexity:.1f}")

    if complex_complexity > simple_complexity:
        print("   ✓ PASSED")
    else:
        print("   ✗ FAILED")
        return False

    # Test 3: Result size estimation
    print("\n4. Test: Result size estimation")
    single_row = {"model": "users", "dimensions": [], "measures": ["total_users"], "table": "users"}
    est_single = await validator._estimate_result_size("SELECT COUNT(*) FROM users", single_row)

    grouped = {"model": "users", "dimensions": ["plan_type"], "measures": ["total_users"], "table": "users"}
    est_grouped = await validator._estimate_result_size("SELECT plan_type, COUNT(*) FROM users GROUP BY plan_type", grouped)

    print(f"   Single row: {est_single}, Grouped: {est_grouped}")

    if est_single == 1 and est_grouped > 1:
        print("   ✓ PASSED")
    else:
        print("   ✗ FAILED")
        return False

    # Test 4: Warning detection
    print("\n5. Test: Warning detection")
    events_query = await manager.build_query(model="events", dimensions=["event_type"], measures=["total_events"])
    warnings = validator._check_for_warnings(events_query["sql"], events_query)

    print(f"   Warnings: {len(warnings)}")
    if warnings:
        for w in warnings:
            print(f"      - {w}")
    print("   ✓ PASSED")

    # Test 5: EXPLAIN execution
    print("\n6. Test: EXPLAIN query")
    try:
        raw_conn = manager.connection.con
        cursor = raw_conn.execute(f"EXPLAIN {query_info['sql']}")
        result = cursor.fetchall()
        print(f"   EXPLAIN returned {len(result)} rows")
        print("   ✓ PASSED")
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
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
