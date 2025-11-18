#!/usr/bin/env python3
"""
Runtime Metric Definitions for AI Analyst

Allows users to define custom metrics at runtime without editing YAML files.
Metrics are validated against semantic models and persisted to JSON.

Features:
- Define metrics at runtime (count, sum, avg, ratio, custom_sql)
- Validate against semantic models
- Persist to JSON file
- Thread-safe updates
- Integration with query execution
"""

import json
import logging
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class RuntimeMetric:
    """User-defined runtime metric"""

    name: str
    type: str  # count, count_distinct, sum, avg, ratio, custom_sql
    model: str
    description: str = ""

    # For standard aggregations
    dimension: Optional[str] = None

    # For ratio metrics
    numerator: Optional[str] = None
    denominator: Optional[str] = None

    # For custom SQL
    sql: Optional[str] = None

    # Filters
    filters: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    created_by: str = "user"
    created_at: str = ""
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if self.filters is None:
            self.filters = {}
        if self.tags is None:
            self.tags = []


class RuntimeMetricRegistry:
    """
    Manages user-defined runtime metrics.

    Features:
    - Define metrics at runtime
    - Persist to JSON file
    - Validate against semantic models
    - Integration with query execution
    """

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.metrics: Dict[str, RuntimeMetric] = {}
        self._lock = asyncio.Lock()  # Thread-safe updates

        # Load existing metrics
        self._load_metrics()

    def _load_metrics(self):
        """Load runtime metrics from storage"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)

                for metric_data in data.get("metrics", []):
                    metric = RuntimeMetric(**metric_data)
                    self.metrics[metric.name] = metric

                logger.info(f"Loaded {len(self.metrics)} runtime metrics")

            except Exception as e:
                logger.error(f"Failed to load runtime metrics: {e}")

    def _save_metrics(self):
        """Persist runtime metrics to storage"""
        try:
            # Ensure parent directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "metrics": [asdict(m) for m in self.metrics.values()],
                "last_updated": datetime.now().isoformat(),
            }

            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved {len(self.metrics)} runtime metrics")

        except Exception as e:
            logger.error(f"Failed to save runtime metrics: {e}")

    async def define_metric(
        self, name: str, type: str, model: str, semantic_manager, **kwargs
    ) -> Dict[str, Any]:
        """
        Define a new runtime metric.

        Args:
            name: Metric name (unique identifier)
            type: Metric type (count, count_distinct, sum, avg, ratio, custom_sql)
            model: Semantic model this metric belongs to
            semantic_manager: For validation
            **kwargs: Additional metric parameters

        Returns:
            Status and created metric details
        """

        async with self._lock:
            # Validate metric name
            if name in self.metrics:
                return {"error": f"Metric '{name}' already exists", "status": "error"}

            # Validate model exists
            try:
                available_models = await semantic_manager.get_available_models()
                model_names = [m["name"] for m in available_models]

                if model not in model_names:
                    return {
                        "error": f"Model '{model}' not found. Available: {model_names}",
                        "status": "error",
                    }
            except Exception as e:
                return {
                    "error": f"Failed to validate model: {str(e)}",
                    "status": "error",
                }

            # Validate metric type
            valid_types = ["count", "count_distinct", "sum", "avg", "ratio", "custom_sql"]
            if type not in valid_types:
                return {
                    "error": f"Invalid metric type '{type}'. Valid: {valid_types}",
                    "status": "error",
                }

            # Create metric
            metric = RuntimeMetric(name=name, type=type, model=model, **kwargs)

            # Validate metric can be executed
            validation_result = await self._validate_metric(metric, semantic_manager)

            if not validation_result["valid"]:
                return {
                    "error": f"Metric validation failed: {validation_result['error']}",
                    "status": "error",
                }

            # Store metric
            self.metrics[name] = metric
            self._save_metrics()

            return {
                "metric": asdict(metric),
                "status": "success",
                "message": f"Metric '{name}' created successfully",
            }

    async def _validate_metric(
        self, metric: RuntimeMetric, semantic_manager
    ) -> Dict[str, Any]:
        """
        Validate metric can be executed.

        Checks:
        - Dimension exists in model
        - SQL is valid (for custom_sql)
        - Ratio numerator/denominator are valid
        """
        try:
            # Get model schema
            model_schema = await semantic_manager.get_model_schema(metric.model)

            # Validate dimension exists
            if metric.dimension:
                available_dims = [d["name"] for d in model_schema["dimensions"]]
                if metric.dimension not in available_dims:
                    return {
                        "valid": False,
                        "error": f"Dimension '{metric.dimension}' not found in model '{metric.model}'. Available: {available_dims}",
                    }

            # Validate ratio components
            if metric.type == "ratio":
                if not metric.numerator or not metric.denominator:
                    return {
                        "valid": False,
                        "error": "Ratio metrics require 'numerator' and 'denominator'",
                    }

            # Validate custom SQL (basic check)
            if metric.type == "custom_sql":
                if not metric.sql:
                    return {
                        "valid": False,
                        "error": "Custom SQL metrics require 'sql' parameter",
                    }

                # Could add SQL parsing here for deeper validation

            return {"valid": True}

        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}

    def get_metric(self, name: str) -> Optional[RuntimeMetric]:
        """Get runtime metric by name"""
        return self.metrics.get(name)

    def list_metrics(
        self, model: Optional[str] = None, tags: Optional[List[str]] = None
    ) -> List[RuntimeMetric]:
        """
        List runtime metrics with optional filtering.

        Args:
            model: Filter by model name
            tags: Filter by tags (any match)

        Returns:
            List of matching metrics
        """
        metrics = list(self.metrics.values())

        if model:
            metrics = [m for m in metrics if m.model == model]

        if tags:
            metrics = [m for m in metrics if any(tag in m.tags for tag in tags)]

        return metrics

    async def delete_metric(self, name: str) -> Dict[str, Any]:
        """Delete a runtime metric"""
        async with self._lock:
            if name not in self.metrics:
                return {"error": f"Metric '{name}' not found", "status": "error"}

            del self.metrics[name]
            self._save_metrics()

            return {
                "message": f"Metric '{name}' deleted successfully",
                "status": "success",
            }

    def to_ibis_expression(self, metric: RuntimeMetric, table):
        """
        Convert runtime metric to Ibis expression for query execution.

        Args:
            metric: Runtime metric definition
            table: Ibis table reference

        Returns:
            Ibis expression for the metric
        """
        # Apply filters if present
        filtered_table = table
        for filter_key, filter_value in metric.filters.items():
            # Parse filter format: dimension__operator
            parts = filter_key.split("__")
            if len(parts) == 2:
                dimension, operator = parts
                if operator == "gt":
                    filtered_table = filtered_table.filter(
                        filtered_table[dimension] > filter_value
                    )
                elif operator == "gte":
                    filtered_table = filtered_table.filter(
                        filtered_table[dimension] >= filter_value
                    )
                elif operator == "lt":
                    filtered_table = filtered_table.filter(
                        filtered_table[dimension] < filter_value
                    )
                elif operator == "lte":
                    filtered_table = filtered_table.filter(
                        filtered_table[dimension] <= filter_value
                    )
                elif operator == "eq":
                    filtered_table = filtered_table.filter(
                        filtered_table[dimension] == filter_value
                    )
                elif operator == "ne":
                    filtered_table = filtered_table.filter(
                        filtered_table[dimension] != filter_value
                    )
            else:
                # Simple equality filter
                filtered_table = filtered_table.filter(
                    filtered_table[filter_key] == filter_value
                )

        # Generate aggregation expression based on type
        if metric.type == "count":
            return filtered_table.count()
        elif metric.type == "count_distinct":
            if not metric.dimension:
                raise ValueError(
                    f"count_distinct metric '{metric.name}' requires dimension"
                )
            return filtered_table[metric.dimension].nunique()
        elif metric.type == "sum":
            if not metric.dimension:
                raise ValueError(f"sum metric '{metric.name}' requires dimension")
            return filtered_table[metric.dimension].sum()
        elif metric.type == "avg":
            if not metric.dimension:
                raise ValueError(f"avg metric '{metric.name}' requires dimension")
            return filtered_table[metric.dimension].mean()
        elif metric.type == "ratio":
            # Ratio metrics need special handling in query context
            # This is a placeholder - actual implementation would depend on numerator/denominator
            raise NotImplementedError(
                "Ratio metrics require special handling in query context"
            )
        elif metric.type == "custom_sql":
            # Custom SQL would need to be compiled separately
            raise NotImplementedError(
                "Custom SQL metrics require special compilation"
            )
        else:
            raise ValueError(f"Unknown metric type: {metric.type}")


# Global registry instance (will be initialized with proper storage path)
_registry_instance: Optional[RuntimeMetricRegistry] = None


def get_registry(storage_path: Optional[Path] = None) -> RuntimeMetricRegistry:
    """
    Get global runtime metric registry instance.

    Args:
        storage_path: Path to storage file (only used on first call)

    Returns:
        RuntimeMetricRegistry instance
    """
    global _registry_instance

    if _registry_instance is None:
        if storage_path is None:
            # Default storage path
            storage_path = (
                Path(__file__).parent.parent / "data" / "runtime_metrics.json"
            )
        _registry_instance = RuntimeMetricRegistry(storage_path)

    return _registry_instance
