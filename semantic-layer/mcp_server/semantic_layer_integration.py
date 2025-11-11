#!/usr/bin/env python3
"""
Semantic Layer Integration for AI Analyst

Integrates with Boring Semantic Layer and Ibis to provide
query building and execution capabilities.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import ibis
import numpy as np
import pandas as pd
import yaml

logger = logging.getLogger(__name__)


class SemanticLayerManager:
    """Manages semantic layer models and query execution"""

    def __init__(self):
        self.connection = None
        self.models = {}
        self.models_path = Path(__file__).parent.parent / "models"
        self.db_path = Path(__file__).parent.parent / "data" / "analytics.duckdb"
        self._models_list_cache = None  # Cache for list_available_models()

    async def initialize(self):
        """Initialize database connection and load semantic models"""
        # Connect to DuckDB
        self.connection = ibis.duckdb.connect(str(self.db_path))

        # Load semantic models
        await self._load_models()

        logger.info(f"Loaded {len(self.models)} semantic models")

    async def _load_models(self):
        """Load YAML semantic model definitions"""
        # Invalidate cache when reloading models
        self._models_list_cache = None

        for model_file in self.models_path.glob("*.yml"):
            try:
                with open(model_file, "r") as f:
                    model_config = yaml.safe_load(f)

                model_name = model_config["model"]["name"]
                self.models[model_name] = model_config

            except Exception as e:
                logger.error(f"Failed to load model {model_file}: {e}")

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available semantic models"""
        models = []

        for name, config in self.models.items():
            model_info = config["model"]

            # Count dimensions and measures
            dimensions = config.get("dimensions", [])
            measures = config.get("measures", [])

            models.append(
                {
                    "name": name,
                    "description": model_info.get("description", ""),
                    "table": model_info.get("table", ""),
                    "dimensions_count": len(dimensions),
                    "measures_count": len(measures),
                    "sample_queries_count": len(config.get("sample_queries", [])),
                }
            )

        return models

    async def list_available_models(self) -> List[Dict[str, Any]]:
        """
        List all available semantic models with complete metadata.

        This method includes intelligent caching to improve performance for repeated calls.
        Models are loaded from YAML files and enriched with dimension, measure, and
        relationship information.

        Returns:
            List[Dict]: List of model dictionaries with:
                - name: Model name
                - description: Model description
                - dimensions: List of dimension names
                - measures: List of measure names
                - relationships: List of related model names (based on foreign keys)

        Example:
            [
                {
                    "name": "users",
                    "description": "User demographics and account details",
                    "dimensions": ["user_id", "plan_type", "industry"],
                    "measures": ["total_users", "paid_users", "conversion_rate"],
                    "relationships": []
                },
                {
                    "name": "events",
                    "description": "User actions and feature usage",
                    "dimensions": ["event_id", "user_id", "event_type"],
                    "measures": ["total_events", "unique_users"],
                    "relationships": ["users", "sessions"]
                }
            ]

        Performance:
            - First call: ~10-50ms (loads and processes YAML files)
            - Cached calls: <1ms (returns cached result)
            - Cache invalidated on: model reload or manager reinitialization
        """
        # Return cached result if available
        if self._models_list_cache is not None:
            logger.debug(f"Returning cached model list ({len(self._models_list_cache)} models)")
            return self._models_list_cache

        logger.info(f"Building model list from {len(self.models)} loaded models")
        models = []

        try:
            for name, config in self.models.items():
                try:
                    model_info = config.get("model", {})

                    # Extract dimension names with error handling
                    dimensions = config.get("dimensions", [])
                    dimension_names = []
                    for dim in dimensions:
                        if isinstance(dim, dict) and "name" in dim:
                            dimension_names.append(dim["name"])
                        else:
                            logger.warning(f"Invalid dimension format in model '{name}': {dim}")

                    # Extract measure names with error handling
                    measures = config.get("measures", [])
                    measure_names = []
                    for measure in measures:
                        if isinstance(measure, dict) and "name" in measure:
                            measure_names.append(measure["name"])
                        else:
                            logger.warning(f"Invalid measure format in model '{name}': {measure}")

                    # Extract relationships by finding foreign keys
                    relationships = []
                    for dim in dimensions:
                        if isinstance(dim, dict) and "foreign_key" in dim:
                            try:
                                # foreign_key format is "table.column"
                                foreign_key = dim["foreign_key"]
                                if isinstance(foreign_key, str) and "." in foreign_key:
                                    foreign_table = foreign_key.split(".")[0]
                                    if foreign_table not in relationships and foreign_table != name:
                                        relationships.append(foreign_table)
                            except Exception as e:
                                logger.warning(f"Error parsing foreign key in model '{name}': {e}")

                    # Build model dictionary
                    model_dict = {
                        "name": name,
                        "description": model_info.get("description", ""),
                        "dimensions": dimension_names,
                        "measures": measure_names,
                        "relationships": sorted(relationships),  # Sort for consistency
                    }

                    models.append(model_dict)
                    logger.debug(
                        f"Processed model '{name}': "
                        f"{len(dimension_names)} dimensions, "
                        f"{len(measure_names)} measures, "
                        f"{len(relationships)} relationships"
                    )

                except Exception as e:
                    logger.error(f"Error processing model '{name}': {e}", exc_info=True)
                    # Continue processing other models even if one fails

            # Sort models by name for consistent ordering
            models.sort(key=lambda m: m["name"])

            # Cache the result
            self._models_list_cache = models
            logger.info(f"Successfully built and cached list of {len(models)} models")

        except Exception as e:
            logger.error(f"Critical error building model list: {e}", exc_info=True)
            # Return empty list on critical error rather than crashing
            return []

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
            "validation": config.get("validation", {}),
        }

    async def build_query(
        self,
        model: str,
        dimensions: List[str] = [],
        measures: List[str] = [],
        filters: Dict[str, Any] = {},
        limit: Optional[int] = None,
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
                    select_parts.append(
                        f"COUNT(DISTINCT CASE WHEN plan_type != 'free' THEN user_id END) * 100.0 / COUNT(DISTINCT user_id) as {measure}"
                    )
                else:
                    # Generic ratio calculation with proper handling
                    ratio_sql = self._build_ratio_calculation(
                        numerator, denominator, table_name, measure
                    )
                    select_parts.append(ratio_sql)

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
        elif model == "events" and any(
            dim.startswith("plan_") or dim.startswith("industry") for dim in dimensions
        ):
            # Join events with users for demographic analysis
            from_clause = f"{table_name} e JOIN users u ON e.user_id = u.user_id"
            # Update select parts to use proper table aliases
            select_parts = [
                part.replace("plan_type", "u.plan_type").replace(
                    "industry", "u.industry"
                )
                for part in select_parts
            ]

        # Build WHERE clause
        where_conditions = []
        for key, value in filters.items():
            if isinstance(value, str):
                where_conditions.append(f"{key} = '{value}'")
            elif isinstance(value, list):
                quoted_values = [
                    f"'{v}'" if isinstance(v, str) else str(v) for v in value
                ]
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
        where_clause = (
            f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""
        )

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
            "table": table_name,
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
            # Must convert NumPy types to native Python types for MCP serialization
            data = []
            for row in result_df.to_dict("records"):
                converted_row = {}
                for key, value in row.items():
                    # Convert NumPy types to native Python types
                    if isinstance(value, np.integer):
                        converted_row[key] = int(value)
                    elif isinstance(value, np.floating):
                        converted_row[key] = float(value)
                    elif isinstance(value, np.bool_):
                        converted_row[key] = bool(value)
                    elif pd.isna(value):
                        converted_row[key] = None
                    else:
                        converted_row[key] = value
                data.append(converted_row)

            # Calculate basic statistics
            row_count = len(data)
            column_count = len(result_df.columns) if row_count > 0 else 0

            return {
                "data": data,
                "columns": list(result_df.columns),
                "row_count": row_count,
                "column_count": column_count,
                "execution_time_ms": round(execution_time * 1000, 2),
                "timestamp": datetime.now().isoformat(),
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
                "timestamp": datetime.now().isoformat(),
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
                "models_loaded": len(self.models),
            }

            return {
                "database_connected": True,
                "database_info": db_info,
                "models_count": len(self.models),
                "test_query_result": result.iloc[0]["test_count"],
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "database_connected": False,
                "error": str(e),
                "models_count": len(self.models),
                "timestamp": datetime.now().isoformat(),
            }

    def _build_ratio_calculation(
        self, numerator: str, denominator: str, table_name: str, measure_name: str
    ) -> str:
        """Build SQL for generic ratio calculation"""

        # Map common measure names to their SQL calculations
        measure_mappings = {
            # User metrics
            "active_users": "COUNT(DISTINCT CASE WHEN last_activity_date >= DATE('now', '-30 days') THEN user_id END)",
            "total_users": "COUNT(DISTINCT user_id)",
            "paid_users": "COUNT(DISTINCT CASE WHEN plan_type != 'free' THEN user_id END)",
            "free_users": "COUNT(DISTINCT CASE WHEN plan_type = 'free' THEN user_id END)",
            # Event metrics
            "total_events": "COUNT(*)",
            "unique_events": "COUNT(DISTINCT event_id)",
            "conversion_events": "COUNT(DISTINCT CASE WHEN event_type = 'conversion' THEN event_id END)",
            # Engagement metrics
            "sessions": "COUNT(DISTINCT session_id)",
            "daily_sessions": "COUNT(DISTINCT session_id) / COUNT(DISTINCT DATE(created_at))",
            "weekly_sessions": "COUNT(DISTINCT session_id) / (COUNT(DISTINCT DATE(created_at)) / 7.0)",
            # Revenue metrics
            "total_revenue": "SUM(COALESCE(revenue, 0))",
            "average_revenue": "AVG(COALESCE(revenue, 0))",
            "monthly_revenue": "SUM(CASE WHEN created_at >= DATE('now', '-30 days') THEN COALESCE(revenue, 0) ELSE 0 END)",
        }

        # Get SQL for numerator and denominator
        numerator_sql = measure_mappings.get(numerator, f"COUNT(DISTINCT {numerator})")
        denominator_sql = measure_mappings.get(
            denominator, f"COUNT(DISTINCT {denominator})"
        )

        # Handle special cases for common ratios
        if numerator in ["paid_users", "active_users"] and denominator == "total_users":
            # Convert to percentage
            ratio_sql = f"({numerator_sql}) * 100.0 / NULLIF(({denominator_sql}), 0) as {measure_name}"
        elif "revenue" in numerator and "users" in denominator:
            # Revenue per user metrics
            ratio_sql = (
                f"({numerator_sql}) / NULLIF(({denominator_sql}), 0) as {measure_name}"
            )
        elif "events" in numerator and "sessions" in denominator:
            # Events per session
            ratio_sql = (
                f"({numerator_sql}) / NULLIF(({denominator_sql}), 0) as {measure_name}"
            )
        elif "sessions" in numerator and "users" in denominator:
            # Sessions per user
            ratio_sql = (
                f"({numerator_sql}) / NULLIF(({denominator_sql}), 0) as {measure_name}"
            )
        else:
            # Generic ratio calculation
            ratio_sql = f"({numerator_sql}) * 1.0 / NULLIF(({denominator_sql}), 0) as {measure_name}"

        return ratio_sql

    async def cleanup(self):
        """Clean up database connections"""
        if self.connection:
            self.connection.disconnect()
            self.connection = None
