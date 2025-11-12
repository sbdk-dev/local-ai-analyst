#!/usr/bin/env python3
"""
MCP Tools for Query Validation

These tools should be added to server.py to enable query validation
via the MCP protocol.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# NOTE: These functions should be added to server.py with the @mcp.tool() decorator

async def validate_query_tool(
    model: str,
    dimensions: List[str] = [],
    measures: List[str] = [],
    filters: Dict[str, Any] = {},
    limit: Optional[int] = None,
    semantic_manager=None,
    query_validator=None,
) -> Dict[str, Any]:
    """
    Validate a query without executing it.

    This tool performs dry-run validation to catch errors before expensive execution.
    It checks query complexity, estimates result size, and provides warnings.

    Args:
        model: Semantic model name (e.g., "users", "events")
        dimensions: List of dimension names to group by
        measures: List of measure names to calculate
        filters: Optional filters to apply
        limit: Optional row limit
        semantic_manager: SemanticLayerManager instance (injected)
        query_validator: QueryValidator instance (injected)

    Returns:
        Validation result with complexity score, estimated rows, and warnings

    Example:
        validate_query_tool(
            model="events",
            dimensions=["event_type", "feature_name", "user_id"],
            measures=["total_events", "unique_users"]
        )

        Returns:
        {
            "valid": false,
            "error": "Query too complex (score: 36.0/30.0). Consider adding filters or reducing dimensions.",
            "complexity_score": 36.0,
            "estimated_rows": null,
            "warnings": [],
            "query_info": {
                "model": "events",
                "dimensions": [...],
                "measures": [...]
            }
        }
    """
    try:
        logger.info(
            f"Validating query for model '{model}' with {len(dimensions)} dimensions, {len(measures)} measures"
        )

        # Build query
        query_info = await semantic_manager.build_query(
            model=model,
            dimensions=dimensions,
            measures=measures,
            filters=filters,
            limit=limit,
        )

        # Create Ibis expression
        ibis_expr = semantic_manager.connection.sql(query_info["sql"])

        # Validate
        validation_result = await query_validator.validate_ibis_query(
            ibis_expr, query_info
        )

        # Return validation result
        result = {
            "valid": validation_result.valid,
            "error": validation_result.error,
            "complexity_score": validation_result.complexity_score,
            "estimated_rows": validation_result.estimated_rows,
            "warnings": validation_result.warnings,
            "query_info": {
                "model": model,
                "dimensions": dimensions,
                "measures": measures,
                "filters": filters,
                "limit": limit,
                "sql": query_info["sql"],
            },
        }

        if validation_result.valid:
            logger.info(
                f"Query validation passed: complexity={validation_result.complexity_score:.1f}, "
                f"estimated_rows={validation_result.estimated_rows}"
            )
        else:
            logger.warning(
                f"Query validation failed: {validation_result.error}"
            )

        return result

    except Exception as e:
        logger.error(f"Error validating query: {e}", exc_info=True)
        return {
            "valid": False,
            "error": f"Validation error: {str(e)}",
            "complexity_score": 0.0,
            "estimated_rows": None,
            "warnings": [],
        }


async def get_validation_settings_tool(query_validator=None) -> Dict[str, Any]:
    """
    Get current validation settings and thresholds.

    Returns the configuration of the query validator including complexity
    thresholds and result size limits.

    Args:
        query_validator: QueryValidator instance (injected)

    Returns:
        Current validation settings

    Example:
        {
            "max_complexity": 80.0,
            "max_estimated_rows": 100000,
            "validation_enabled": true
        }
    """
    try:
        if not query_validator:
            return {
                "error": "Query validator not initialized",
                "validation_enabled": False,
            }

        return {
            "max_complexity": query_validator.max_complexity,
            "max_estimated_rows": query_validator.max_estimated_rows,
            "validation_enabled": True,
            "description": "Query validation prevents expensive queries by checking complexity and result size before execution",
        }

    except Exception as e:
        logger.error(f"Error getting validation settings: {e}", exc_info=True)
        return {"error": str(e), "validation_enabled": False}


# Integration instructions for server.py:
"""
To integrate these tools into server.py, add the following:

1. Import QueryValidator at the top of server.py:
   from .query_validator import QueryValidator

2. Initialize QueryValidator in the server initialization:
   query_validator = QueryValidator(semantic_manager.connection)

3. Add MCP tools:

   @mcp.tool()
   @error_handler("validate_query")
   async def validate_query(
       model: str,
       dimensions: List[str] = [],
       measures: List[str] = [],
       filters: Dict[str, Any] = {},
       limit: Optional[int] = None,
   ) -> Dict[str, Any]:
       '''Validate a query without executing it'''
       return await validate_query_tool(
           model=model,
           dimensions=dimensions,
           measures=measures,
           filters=filters,
           limit=limit,
           semantic_manager=semantic_manager,
           query_validator=query_validator,
       )

   @mcp.tool()
   @error_handler("get_validation_settings")
   async def get_validation_settings() -> Dict[str, Any]:
       '''Get current validation settings'''
       return await get_validation_settings_tool(query_validator=query_validator)

4. Update the query_model tool to support optional validation:

   Add an optional parameter to query_model:
       validate_before_execution: bool = False

   Then before executing, add:
       if validate_before_execution:
           result = await semantic_manager.execute_query(
               query_info, validate=True, validator=query_validator
           )
       else:
           result = await semantic_manager.execute_query(query_info)

This enables:
- Manual query validation via validate_query tool
- Optional validation in query_model tool
- Checking validation settings via get_validation_settings tool
"""
