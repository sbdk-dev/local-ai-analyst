#!/usr/bin/env python3
"""
Semantic Layer Integration for AI Analyst

Integrates with Boring Semantic Layer and Ibis to provide
query building and execution capabilities.
"""

import time
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

import ibis
import pandas as pd
from datetime import datetime

class SemanticLayerManager:
    """Manages semantic layer models and query execution"""

    def __init__(self):
        self.connection = None
        self.models = {}
        self.models_path = Path(__file__).parent.parent / "models"
        self.db_path = Path(__file__).parent.parent / "data" / "analytics.duckdb"

    async def initialize(self):
        """Initialize database connection and load semantic models"""
        # Connect to DuckDB
        self.connection = ibis.duckdb.connect(str(self.db_path))

        # Load semantic models
        await self._load_models()

        print(f"Loaded {len(self.models)} semantic models")

    async def _load_models(self):
        """Load YAML semantic model definitions"""
        for model_file in self.models_path.glob("*.yml"):
            try:
                with open(model_file, 'r') as f:
                    model_config = yaml.safe_load(f)

                model_name = model_config["model"]["name"]
                self.models[model_name] = model_config

            except Exception as e:
                print(f"Failed to load model {model_file}: {e}")

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available semantic models"""
        models = []

        for name, config in self.models.items():
            model_info = config["model"]

            # Count dimensions and measures
            dimensions = config.get("dimensions", [])
            measures = config.get("measures", [])

            models.append({
                "name": name,
                "description": model_info.get("description", ""),
                "table": model_info.get("table", ""),
                "dimensions_count": len(dimensions),
                "measures_count": len(measures),
                "sample_queries_count": len(config.get("sample_queries", []))
            })

        return models

    async def get_model_schema(self, model_name: str) -> Dict[str, Any]:
        """Get detailed schema for a specific model"""
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found")

        config = self.models[model_name]

        return {
            "model": config["model"],
            "dimensions": config.get("dimensions", []),
            "measures": config.get("measures", []),
            "context": config.get("context", {}),
            "sample_queries": config.get("sample_queries", []),
            "validation": config.get("validation", {})
        }

    async def build_query(
        self,
        model: str,
        dimensions: List[str] = [],
        measures: List[str] = [],
        filters: Dict[str, Any] = {},
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Build SQL query from semantic model specification"""

        if model not in self.models:
            raise ValueError(f"Model '{model}' not found")

        config = self.models[model]
        table_name = config["model"]["table"]

        # Validate dimensions and measures exist
        available_dimensions = {d["name"]: d for d in config.get("dimensions", [])}
        available_measures = {m["name"]: m for m in config.get("measures", [])}

        for dim in dimensions:
            if dim not in available_dimensions:
                raise ValueError(f"Dimension '{dim}' not found in model '{model}'")

        for measure in measures:
            if measure not in available_measures:
                raise ValueError(f"Measure '{measure}' not found in model '{model}'")

        # Build SELECT clause
        select_parts = []

        # Add dimensions
        for dim in dimensions:
            dim_config = available_dimensions[dim]
            if "sql" in dim_config:
                select_parts.append(f"({dim_config['sql']}) as {dim}")
            else:
                select_parts.append(dim)

        # Add measures
        for measure in measures:
            measure_config = available_measures[measure]

            if measure_config["type"] == "count":
                select_parts.append(f"COUNT(*) as {measure}")

            elif measure_config["type"] == "count_distinct":
                dimension_col = measure_config.get("dimension", "id")
                select_parts.append(f"COUNT(DISTINCT {dimension_col}) as {measure}")

            elif measure_config["type"] == "ratio":
                # For ratio measures, calculate numerator/denominator
                numerator = measure_config.get("numerator")
                denominator = measure_config.get("denominator")

                if numerator == "paid_users" and denominator == "total_users":
                    # Special case for conversion rate
                    select_parts.append(f"COUNT(DISTINCT CASE WHEN plan_type != 'free' THEN user_id END) * 100.0 / COUNT(DISTINCT user_id) as {measure}")
                else:
                    # Generic ratio - would need more sophisticated handling in real implementation
                    select_parts.append(f"0.0 as {measure}  -- ratio calculation not implemented")

            elif "sql" in measure_config:
                select_parts.append(f"({measure_config['sql']}) as {measure}")

        # If no dimensions or measures specified, do basic count
        if not select_parts:
            select_parts = ["COUNT(*) as total_rows"]

        # Build FROM clause
        from_clause = table_name

        # Add joins if this is a multi-table model
        if model == "engagement":
            # Special handling for engagement model which joins multiple tables
            from_clause = """
                users u
                LEFT JOIN events e ON u.user_id = e.user_id
                LEFT JOIN sessions s ON u.user_id = s.user_id
            """
        elif model == "events" and any(dim.startswith("plan_") or dim.startswith("industry") for dim in dimensions):
            # Join events with users for demographic analysis
            from_clause = f"{table_name} e JOIN users u ON e.user_id = u.user_id"
            # Update select parts to use proper table aliases
            select_parts = [part.replace("plan_type", "u.plan_type").replace("industry", "u.industry")
                          for part in select_parts]

        # Build WHERE clause
        where_conditions = []
        for key, value in filters.items():
            if isinstance(value, str):
                where_conditions.append(f"{key} = '{value}'")
            elif isinstance(value, list):
                quoted_values = [f"'{v}'" if isinstance(v, str) else str(v) for v in value]
                where_conditions.append(f"{key} IN ({', '.join(quoted_values)})")
            else:
                where_conditions.append(f"{key} = {value}")

        # Build GROUP BY clause
        group_by_clause = ""
        if dimensions:
            group_by_clause = f"GROUP BY {', '.join(dimensions)}"

        # Build ORDER BY clause (order by first measure desc)
        order_by_clause = ""
        if measures:
            order_by_clause = f"ORDER BY {measures[0]} DESC"
        elif dimensions:
            order_by_clause = f"ORDER BY {dimensions[0]}"

        # Build LIMIT clause
        limit_clause = f"LIMIT {limit}" if limit else ""

        # Assemble final query
        where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""

        sql = f"""
        SELECT {', '.join(select_parts)}
        FROM {from_clause}
        {where_clause}
        {group_by_clause}
        {order_by_clause}
        {limit_clause}
        """.strip()

        return {
            "sql": sql,
            "model": model,
            "dimensions": dimensions,
            "measures": measures,
            "filters": filters,
            "table": table_name
        }

    async def execute_query(self, query_info: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SQL query and return results with metadata"""

        sql = query_info["sql"]
        start_time = time.time()

        try:
            # Execute query using Ibis
            result_df = self.connection.sql(sql).to_pandas()

            execution_time = time.time() - start_time

            # Convert DataFrame to records for JSON serialization
            data = result_df.to_dict('records')

            # Calculate basic statistics
            row_count = len(data)
            column_count = len(result_df.columns) if row_count > 0 else 0

            return {
                "data": data,
                "columns": list(result_df.columns),
                "row_count": row_count,
                "column_count": column_count,
                "execution_time_ms": round(execution_time * 1000, 2),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            execution_time = time.time() - start_time

            return {
                "error": str(e),
                "data": [],
                "columns": [],
                "row_count": 0,
                "column_count": 0,
                "execution_time_ms": round(execution_time * 1000, 2),
                "timestamp": datetime.now().isoformat()
            }

    async def get_sample_queries(self, model: str) -> List[Dict[str, Any]]:
        """Get sample queries for a model"""
        if model not in self.models:
            raise ValueError(f"Model '{model}' not found")

        config = self.models[model]
        return config.get("sample_queries", [])

    async def health_check(self) -> Dict[str, Any]:
        """Check health of database connection and semantic layer"""

        try:
            # Test database connection
            test_query = "SELECT COUNT(*) as test_count FROM users LIMIT 1"
            result = self.connection.sql(test_query).to_pandas()

            # Get database info
            db_info = {
                "file_size_mb": round(self.db_path.stat().st_size / (1024 * 1024), 2),
                "tables": ["users", "events", "sessions"],
                "models_loaded": len(self.models)
            }

            return {
                "database_connected": True,
                "database_info": db_info,
                "models_count": len(self.models),
                "test_query_result": result.iloc[0]["test_count"],
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "database_connected": False,
                "error": str(e),
                "models_count": len(self.models),
                "timestamp": datetime.now().isoformat()
            }

    async def cleanup(self):
        """Clean up database connections"""
        if self.connection:
            self.connection.disconnect()
            self.connection = None