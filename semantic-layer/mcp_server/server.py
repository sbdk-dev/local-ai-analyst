#!/usr/bin/env python3
"""
FastMCP Server for AI Analyst System

Connects Claude Desktop to semantic layer via MCP protocol.
Implements execution-first pattern to prevent fabrication.
"""

import asyncio
import json
import logging
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("ai_analyst.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

from .conversation_memory import ConversationMemory
from .intelligence_layer import IntelligenceEngine
from .model_discovery import ModelDiscovery
from .query_optimizer import QueryOptimizer
from .runtime_metrics import RuntimeMetricRegistry, get_registry
# Import our semantic layer integration
from .semantic_layer_integration import SemanticLayerManager
from .statistical_testing import StatisticalTester
from .workflow_orchestrator import WorkflowOrchestrator

# Initialize components
semantic_manager = SemanticLayerManager()
intelligence_engine = IntelligenceEngine()
statistical_tester = StatisticalTester()
conversation_memory = ConversationMemory()
query_optimizer = QueryOptimizer()
workflow_orchestrator = WorkflowOrchestrator()

# Initialize model discovery with path to semantic models (lazy loading)
models_path = Path(__file__).parent.parent / "models"
model_discovery = ModelDiscovery(models_path, lazy_load=True)

# Initialize runtime metrics registry
runtime_metrics_storage = Path(__file__).parent.parent / "data" / "runtime_metrics.json"
runtime_metrics_registry = get_registry(runtime_metrics_storage)

# MCP server configuration (temporary, will be recreated with lifespan)
mcp = FastMCP("ai-analyst")


def error_handler(operation_name: str, retry_count: int = 2):
    """Decorator for comprehensive error handling and logging"""

    def decorator(func):
        async def wrapper(**kwargs):
            start_time = time.time()
            last_exception = None

            for attempt in range(retry_count + 1):
                try:
                    logger.info(
                        f"Starting {operation_name} (attempt {attempt + 1}/{retry_count + 1})"
                    )
                    result = await func(**kwargs)

                    execution_time = (time.time() - start_time) * 1000
                    logger.info(
                        f"Completed {operation_name} successfully in {execution_time:.2f}ms"
                    )

                    return result

                except Exception as e:
                    last_exception = e
                    execution_time = (time.time() - start_time) * 1000

                    error_details = {
                        "operation": operation_name,
                        "attempt": attempt + 1,
                        "max_attempts": retry_count + 1,
                        "execution_time_ms": execution_time,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "kwargs": {
                            k: v
                            for k, v in kwargs.items()
                            if k not in ["password", "token", "api_key"]
                        },  # Sanitize sensitive data
                    }

                    if attempt < retry_count:
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {operation_name}: {str(e)}. Retrying..."
                        )
                        await asyncio.sleep(
                            min(2**attempt, 10)
                        )  # Exponential backoff with max 10s
                    else:
                        logger.error(
                            f"All attempts failed for {operation_name}: {str(e)}"
                        )
                        logger.error(
                            f"Full error details: {json.dumps(error_details, indent=2)}"
                        )
                        logger.debug(f"Traceback: {traceback.format_exc()}")

            # Return graceful error response instead of crashing
            return {
                "error": True,
                "operation": operation_name,
                "message": f"Operation failed after {retry_count + 1} attempts",
                "last_error": str(last_exception),
                "error_type": type(last_exception).__name__,
                "timestamp": datetime.now().isoformat(),
                "suggestion": "Please check the logs for detailed error information and try again later",
            }

        return wrapper

    return decorator


def validate_inputs(**validators):
    """Decorator for input validation with detailed error messages"""

    def decorator(func):
        async def wrapper(**kwargs):
            validation_errors = []

            for param_name, validator_func in validators.items():
                if param_name in kwargs:
                    try:
                        if not validator_func(kwargs[param_name]):
                            validation_errors.append(
                                f"Invalid {param_name}: {kwargs[param_name]}"
                            )
                    except Exception as e:
                        validation_errors.append(
                            f"Validation error for {param_name}: {str(e)}"
                        )
                elif param_name != "optional":
                    validation_errors.append(
                        f"Missing required parameter: {param_name}"
                    )

            if validation_errors:
                logger.warning(
                    f"Input validation failed for {func.__name__}: {validation_errors}"
                )
                return {
                    "error": True,
                    "validation_errors": validation_errors,
                    "message": "Input validation failed",
                    "timestamp": datetime.now().isoformat(),
                }

            return await func(**kwargs)

        return wrapper

    return decorator


# Validation helper functions
def is_valid_model(model: str) -> bool:
    """Validate model name"""
    return (
        model and len(model) > 0 and model.replace("_", "").replace("-", "").isalnum()
    )


def is_valid_dimensions(dimensions: List[str]) -> bool:
    """Validate dimensions list"""
    return isinstance(dimensions, list) and len(dimensions) <= 10


def is_valid_measures(measures: List[str]) -> bool:
    """Validate measures list"""
    return isinstance(measures, list) and len(measures) <= 20


# ============================================================================
# MCP Tool Models
# ============================================================================


class QueryModelRequest(BaseModel):
    """Request to query a semantic model"""

    model: str
    dimensions: List[str] = []
    measures: List[str] = []
    filters: Dict[str, Any] = {}
    limit: Optional[int] = None


class SuggestAnalysisRequest(BaseModel):
    """Request for analysis suggestions"""

    current_result: Optional[str] = None
    context: Optional[str] = None
    model: Optional[str] = None


class TestSignificanceRequest(BaseModel):
    """Request for statistical testing"""

    data: Dict[str, Any]
    comparison_type: str = "groups"  # groups, correlation, trend
    dimensions: List[str] = []
    measures: List[str] = []


# ============================================================================
# Core MCP Tools
# ============================================================================


@mcp.tool()
async def list_models() -> Dict[str, Any]:
    """
    List available semantic models with their descriptions and key metrics.

    Returns available models that can be queried for data analysis.
    """
    try:
        models = await semantic_manager.get_available_models()

        return {
            "models": models,
            "total_count": len(models),
            "description": "Available semantic models for analysis",
        }

    except Exception as e:
        return {"error": str(e), "message": "Failed to retrieve available models"}


@mcp.tool()
async def get_model(model_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific semantic model.

    Args:
        model_name: Name of the model to inspect

    Returns:
        Model schema including dimensions, measures, and sample queries
    """
    try:
        model_info = await semantic_manager.get_model_schema(model_name)

        return {
            "model": model_name,
            "schema": model_info,
            "sample_queries": model_info.get("sample_queries", []),
        }

    except Exception as e:
        return {
            "error": str(e),
            "message": f"Failed to retrieve model info for '{model_name}'",
        }


@mcp.tool()
async def discover_models_for_question(
    question: str, top_k: int = 3, similarity_threshold: float = 0.3
) -> Dict[str, Any]:
    """
    Discover relevant semantic models for a natural language question using vector similarity.

    Uses lightweight SentenceTransformers to match questions to model descriptions.
    Returns ranked models with similarity scores.

    Args:
        question: User's question in natural language
        top_k: Number of models to suggest (default: 3)
        similarity_threshold: Minimum similarity score 0-1 (default: 0.3)

    Returns:
        Ranked list of relevant models with similarity scores

    Examples:
        Q: "What's our monthly revenue growth?"
        Returns: [
            {"model": "users", "similarity": 0.87, "description": "..."},
            {"model": "events", "similarity": 0.65, "description": "..."},
        ]

        Q: "Show me user churn rates"
        Returns: [
            {"model": "engagement", "similarity": 0.92, "description": "..."},
            {"model": "users", "similarity": 0.58, "description": "..."},
        ]

        Q: "Feature adoption by plan type"
        Returns: [
            {"model": "events", "similarity": 0.88, "description": "..."},
            {"model": "users", "similarity": 0.45, "description": "..."},
        ]
    """
    try:
        # Discover relevant models using vector similarity
        results = await model_discovery.discover_models(
            question, top_k=top_k, similarity_threshold=similarity_threshold
        )

        return {
            "question": question,
            "relevant_models": results,
            "top_model": results[0]["model"] if results else None,
            "status": "success",
            "suggestion": f"Use '{results[0]['model']}' model for this question"
            if results
            else "No models found above similarity threshold",
        }

    except Exception as e:
        logger.error(f"Model discovery failed: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "error": str(e),
            "message": "Failed to discover models for question",
            "status": "error",
        }


@mcp.tool()
async def query_model(
    model: str,
    dimensions: List[str] = [],
    measures: List[str] = [],
    filters: Dict[str, Any] = {},
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Query a semantic model with execution-first pattern to prevent fabrication.

    Args:
        model: Name of the semantic model to query
        dimensions: List of dimensions to group by
        measures: List of measures to calculate
        filters: Optional filters to apply
        limit: Optional limit on number of rows returned

    Returns:
        Query results with statistical analysis and natural language interpretation
    """
    try:
        # CRITICAL: Build → Execute → Annotate pattern (Enhanced with Optimization)
        # 1. BUILD: Generate query
        query_info = await semantic_manager.build_query(
            model=model,
            dimensions=dimensions,
            measures=measures,
            filters=filters,
            limit=limit,
        )

        # 2. OPTIMIZE: Check cache and optimize query
        query_key = query_optimizer.generate_cache_key(query_info)
        cached_result = query_optimizer.get_cached_result(query_key)

        if cached_result:
            result = cached_result
            # Add cache hit metadata
            result["cache_hit"] = True
            result["cache_timestamp"] = cached_result.get("cache_timestamp")
        else:
            # 3. EXECUTE: Run optimized query to get REAL results
            optimized_query = query_optimizer.optimize_query(
                query_info, conversation_memory
            )
            result = await semantic_manager.execute_query(optimized_query)

            # Cache the result
            query_optimizer.cache_result(query_key, result, query_info)
            result["cache_hit"] = False

        # 4. VALIDATE: Check sample sizes and data quality
        validation = await statistical_tester.validate_result(result, dimensions)

        # 5. ANALYZE: Run statistical tests if comparing groups
        statistical_analysis = None
        if len(dimensions) > 0 and len(result.get("data", [])) > 1:
            statistical_analysis = await statistical_tester.auto_test_comparison(
                result, dimensions, measures
            )

        # 6. ANNOTATE: Generate interpretation based on REAL data
        interpretation = await intelligence_engine.generate_interpretation(
            result=result,
            query_info=query_info,
            validation=validation,
            statistical_analysis=statistical_analysis,
        )

        # 7. SUGGEST: Recommend next questions (enhanced with conversation context)
        context_suggestions = await intelligence_engine.suggest_next_questions(
            result=result,
            context=f"querying {model} model",
            current_dimensions=dimensions,
            current_measures=measures,
        )

        # 8. MEMORY: Track this interaction for conversation context
        interaction_id = conversation_memory.add_interaction(
            user_question=f"Query {model} model: {dimensions} x {measures}",
            query_info=query_info,
            result=result,
            insights=[interpretation] if interpretation else [],
            statistical_analysis=statistical_analysis,
        )

        # 9. CONTEXTUAL SUGGESTIONS: Get context-aware recommendations
        contextual_suggestions = conversation_memory.suggest_contextual_next_steps(
            result
        )

        # 10. OPTIMIZATION INSIGHTS: Get performance recommendations
        optimization_insights = query_optimizer.get_optimization_insights(
            query_info, result, conversation_memory
        )

        # Combine suggestions (prioritize contextual ones)
        all_suggestions = contextual_suggestions + context_suggestions
        unique_suggestions = []
        seen_questions = set()

        for suggestion in all_suggestions:
            question = suggestion.get("question", "")
            if question and question not in seen_questions:
                seen_questions.add(question)
                unique_suggestions.append(suggestion)

        return {
            "query": query_info["sql"],
            "result": result,
            "validation": validation,
            "statistical_analysis": statistical_analysis,
            "interpretation": interpretation,
            "suggestions": unique_suggestions[:5],  # Limit to top 5
            "metadata": {
                "model": model,
                "dimensions": dimensions,
                "measures": measures,
                "filters": filters,
                "execution_time_ms": result.get("execution_time_ms", 0),
                "interaction_id": interaction_id,
                "conversation_context": conversation_memory.get_conversation_context(
                    hours_back=2
                ),
                "optimization": {
                    "cache_hit": result.get("cache_hit", False),
                    "cache_timestamp": result.get("cache_timestamp"),
                    "insights": optimization_insights,
                    "query_complexity": query_optimizer.analyze_query_complexity(
                        query_info
                    ),
                },
            },
        }

    except Exception as e:
        # Return error with context for debugging
        return {
            "error": str(e),
            "message": f"Failed to query model '{model}'",
            "query_attempted": {
                "model": model,
                "dimensions": dimensions,
                "measures": measures,
                "filters": filters,
            },
        }


@mcp.tool()
async def suggest_analysis(
    current_result: Optional[str] = None,
    context: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Suggest next analysis steps based on current results or context.

    Args:
        current_result: JSON string of current query result
        context: Description of current analysis context
        model: Current model being analyzed

    Returns:
        Suggested questions and analysis paths
    """
    try:
        # Parse current result if provided
        parsed_result = None
        if current_result:
            try:
                parsed_result = json.loads(current_result)
            except json.JSONDecodeError:
                # If not valid JSON, treat as description
                context = current_result

        suggestions = await intelligence_engine.suggest_analysis_paths(
            current_result=parsed_result, context=context, model=model
        )

        return {"suggestions": suggestions, "context": context, "model": model}

    except Exception as e:
        return {"error": str(e), "message": "Failed to generate analysis suggestions"}


@mcp.tool()
async def test_significance(
    data: Dict[str, Any],
    comparison_type: str = "groups",
    dimensions: List[str] = [],
    measures: List[str] = [],
) -> Dict[str, Any]:
    """
    Run statistical significance tests on data.

    Args:
        data: Query result data to test
        comparison_type: Type of test (groups, correlation, trend)
        dimensions: Dimensions being compared
        measures: Measures being analyzed

    Returns:
        Statistical test results with interpretation
    """
    try:
        test_results = await statistical_tester.run_significance_tests(
            data=data,
            comparison_type=comparison_type,
            dimensions=dimensions,
            measures=measures,
        )

        interpretation = await intelligence_engine.interpret_statistical_results(
            test_results=test_results, dimensions=dimensions, measures=measures
        )

        return {
            "tests": test_results,
            "interpretation": interpretation,
            "metadata": {
                "comparison_type": comparison_type,
                "dimensions": dimensions,
                "measures": measures,
            },
        }

    except Exception as e:
        return {"error": str(e), "message": "Failed to run statistical tests"}


# ============================================================================
# Health Check and Info Tools
# ============================================================================


@mcp.tool()
async def health_check() -> Dict[str, Any]:
    """
    Check health of semantic layer and database connections.

    Returns:
        Health status of all system components
    """
    try:
        health_status = await semantic_manager.health_check()

        return {
            "status": "healthy" if health_status["database_connected"] else "unhealthy",
            "components": health_status,
            "timestamp": health_status.get("timestamp"),
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Health check failed",
        }


@mcp.tool()
async def get_conversation_context() -> Dict[str, Any]:
    """
    Get current conversation context and analysis history.

    Returns conversation themes, analytical focus, and contextual insights
    to enable more sophisticated multi-turn analysis workflows.
    """
    try:
        context = conversation_memory.get_conversation_context()

        return {
            "conversation_context": context,
            "patterns_discovered": conversation_memory.identify_analysis_patterns(),
            "user_interests": conversation_memory.export_conversation_summary().get(
                "user_interests", {}
            ),
            "recommendations": conversation_memory.suggest_contextual_next_steps(),
        }

    except Exception as e:
        return {"error": str(e), "message": "Failed to retrieve conversation context"}


@mcp.tool()
async def get_contextual_suggestions(
    current_focus: Optional[str] = None, hours_back: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get contextual analysis suggestions based on conversation history.

    Args:
        current_focus: Description of current analytical focus
        hours_back: Hours of conversation history to consider

    Returns:
        Contextually relevant next steps and analysis recommendations
    """
    try:
        if hours_back:
            context = conversation_memory.get_conversation_context(hours_back)
        else:
            context = conversation_memory.get_conversation_context()

        suggestions = conversation_memory.suggest_contextual_next_steps()

        return {
            "conversation_context": context,
            "suggested_next_steps": suggestions,
            "analytical_patterns": conversation_memory.identify_analysis_patterns(),
            "focus_areas": context.get("current_analytical_focus", {}),
        }

    except Exception as e:
        return {"error": str(e), "message": "Failed to generate contextual suggestions"}


@mcp.tool()
async def optimize_query(
    model: str,
    dimensions: List[str] = [],
    measures: List[str] = [],
    filters: Dict[str, Any] = {},
) -> Dict[str, Any]:
    """
    Get query optimization recommendations based on conversation history.

    Args:
        model: Name of the semantic model
        dimensions: Proposed dimensions
        measures: Proposed measures
        filters: Proposed filters

    Returns:
        Optimization suggestions and performance recommendations
    """
    try:
        query_info = {
            "model": model,
            "dimensions": dimensions,
            "measures": measures,
            "filters": filters,
        }

        recommendations = conversation_memory.get_query_recommendations(query_info)

        return {
            "query_optimization": recommendations,
            "suggested_additions": {
                "dimensions": recommendations.get("additional_dimensions", [])[:3],
                "measures": recommendations.get("additional_measures", [])[:3],
            },
            "performance_insights": recommendations.get("performance_notes", []),
            "alternative_approaches": recommendations.get("alternative_approaches", []),
        }

    except Exception as e:
        return {
            "error": str(e),
            "message": f"Failed to optimize query for model '{model}'",
        }


@mcp.tool()
async def export_conversation_summary() -> Dict[str, Any]:
    """
    Export a comprehensive summary of the current conversation and analysis.

    Returns detailed conversation metadata, analytical coverage, insights generated,
    and discovered patterns for review or sharing.
    """
    try:
        summary = conversation_memory.export_conversation_summary()

        return {
            "conversation_summary": summary,
            "export_timestamp": datetime.now().isoformat(),
            "status": "success",
        }

    except Exception as e:
        return {"error": str(e), "message": "Failed to export conversation summary"}


@mcp.tool()
async def get_sample_queries(model: str) -> Dict[str, Any]:
    """
    Get sample queries for a specific model to help users get started.

    Args:
        model: Name of the model

    Returns:
        Sample queries with descriptions
    """
    try:
        samples = await semantic_manager.get_sample_queries(model)

        return {"model": model, "sample_queries": samples}

    except Exception as e:
        return {
            "error": str(e),
            "message": f"Failed to get sample queries for model '{model}'",
        }


# ============================================================================
# Query Optimization Tools
# ============================================================================


@mcp.tool()
async def get_query_performance(
    model: str,
    dimensions: List[str] = [],
    measures: List[str] = [],
    hours_back: Optional[int] = 24,
) -> Dict[str, Any]:
    """
    Get performance analytics for similar queries in conversation history.

    Args:
        model: Name of the semantic model
        dimensions: Dimensions to analyze performance for
        measures: Measures to analyze performance for
        hours_back: Hours of history to analyze

    Returns:
        Performance insights and optimization recommendations
    """
    try:
        query_info = {"model": model, "dimensions": dimensions, "measures": measures}

        performance_analysis = query_optimizer.analyze_historical_performance(
            query_info, conversation_memory, hours_back
        )

        optimization_suggestions = query_optimizer.get_optimization_suggestions(
            query_info, conversation_memory
        )

        return {
            "query_pattern": {
                "model": model,
                "dimensions": dimensions,
                "measures": measures,
            },
            "performance_analysis": performance_analysis,
            "optimization_suggestions": optimization_suggestions,
            "cache_status": {
                "cache_size": len(query_optimizer.cache.cache),
                "hit_rate": query_optimizer.get_cache_hit_rate(),
            },
        }

    except Exception as e:
        return {
            "error": str(e),
            "message": f"Failed to analyze query performance for model '{model}'",
        }


@mcp.tool()
async def suggest_batch_queries(
    current_model: str,
    current_dimensions: List[str] = [],
    current_measures: List[str] = [],
) -> Dict[str, Any]:
    """
    Suggest queries that could be batched together for efficiency.

    Args:
        current_model: Current model being queried
        current_dimensions: Current dimensions
        current_measures: Current measures

    Returns:
        Batch optimization opportunities and suggested query combinations
    """
    try:
        current_query = {
            "model": current_model,
            "dimensions": current_dimensions,
            "measures": current_measures,
        }

        batch_opportunities = query_optimizer.identify_batch_opportunities(
            current_query, conversation_memory
        )

        return {
            "current_query": current_query,
            "batch_opportunities": batch_opportunities,
            "efficiency_gains": batch_opportunities.get(
                "estimated_efficiency_improvement", 0
            ),
            "recommended_batches": batch_opportunities.get("recommended_batches", []),
        }

    except Exception as e:
        return {
            "error": str(e),
            "message": f"Failed to suggest batch queries for model '{current_model}'",
        }


@mcp.tool()
async def clear_query_cache(
    selective: bool = False,
    model_filter: Optional[str] = None,
    age_threshold_minutes: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Clear query cache with optional selective clearing.

    Args:
        selective: Whether to clear selectively or all
        model_filter: Only clear cache for specific model
        age_threshold_minutes: Only clear cache older than threshold

    Returns:
        Cache clearing results and statistics
    """
    try:
        cache_stats_before = {
            "size": len(query_optimizer.cache.cache),
            "hit_rate": query_optimizer.get_cache_hit_rate(),
        }

        if selective:
            cleared_count = query_optimizer.cache.selective_clear(
                model_filter=model_filter, age_threshold_minutes=age_threshold_minutes
            )
        else:
            cleared_count = len(query_optimizer.cache.cache)
            query_optimizer.cache.clear()

        cache_stats_after = {
            "size": len(query_optimizer.cache.cache),
            "hit_rate": query_optimizer.get_cache_hit_rate(),
        }

        return {
            "operation": "selective_clear" if selective else "full_clear",
            "filters_applied": {
                "model_filter": model_filter,
                "age_threshold_minutes": age_threshold_minutes,
            },
            "cleared_entries": cleared_count,
            "cache_stats": {"before": cache_stats_before, "after": cache_stats_after},
        }

    except Exception as e:
        return {"error": str(e), "message": "Failed to clear query cache"}


@mcp.tool()
async def get_optimization_dashboard() -> Dict[str, Any]:
    """
    Get comprehensive optimization dashboard with performance metrics.

    Returns:
        Complete optimization status, cache performance, and recommendations
    """
    try:
        dashboard_data = {
            "cache_performance": {
                "total_entries": len(query_optimizer.cache.cache),
                "hit_rate": query_optimizer.get_cache_hit_rate(),
                "memory_usage": query_optimizer.get_cache_memory_usage(),
                "oldest_entry": query_optimizer.get_oldest_cache_entry(),
                "newest_entry": query_optimizer.get_newest_cache_entry(),
            },
            "optimization_patterns": query_optimizer.get_optimization_patterns(
                conversation_memory
            ),
            "performance_trends": query_optimizer.get_performance_trends(
                conversation_memory
            ),
            "recommendations": {
                "high_impact": query_optimizer.get_high_impact_optimizations(
                    conversation_memory
                ),
                "quick_wins": query_optimizer.get_quick_optimization_wins(
                    conversation_memory
                ),
                "cache_tuning": query_optimizer.get_cache_tuning_recommendations(),
            },
            "conversation_insights": {
                "query_patterns": conversation_memory.get_query_usage_patterns(),
                "model_preferences": conversation_memory.get_model_usage_stats(),
                "dimension_combinations": conversation_memory.get_popular_dimension_combinations(),
            },
        }

        return {
            "optimization_dashboard": dashboard_data,
            "generated_at": datetime.now().isoformat(),
            "status": "success",
        }

    except Exception as e:
        return {"error": str(e), "message": "Failed to generate optimization dashboard"}


# ============================================================================
# Multi-Query Workflow Tools
# ============================================================================


@mcp.tool()
async def list_workflow_templates() -> Dict[str, Any]:
    """
    List available workflow templates for multi-query analysis.

    Returns:
        Available workflow templates with descriptions and estimated execution times
    """
    try:
        templates = workflow_orchestrator.list_available_workflows()

        return {
            "workflow_templates": templates,
            "total_templates": len(templates.get("available_templates", {})),
            "description": "Multi-query analytical workflow templates",
        }

    except Exception as e:
        return {"error": str(e), "message": "Failed to retrieve workflow templates"}


@mcp.tool()
async def create_workflow(
    template_id: str, customizations: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a new multi-query workflow execution from template.

    Args:
        template_id: ID of the workflow template to use
        customizations: Optional customizations to apply to the template

    Returns:
        Created workflow execution details
    """
    try:
        execution = await workflow_orchestrator.create_workflow(
            template_id=template_id, customizations=customizations or {}
        )

        return {
            "execution_id": execution.execution_id,
            "workflow_id": execution.workflow_id,
            "status": execution.status.value,
            "total_steps": len(execution.definition.steps),
            "created_at": execution.definition.created_at,
            "description": execution.definition.description,
        }

    except Exception as e:
        return {
            "error": str(e),
            "message": f"Failed to create workflow from template '{template_id}'",
        }


@mcp.tool()
async def execute_workflow(execution_id: str) -> Dict[str, Any]:
    """
    Execute a multi-query workflow with dependency resolution and optimization.

    Args:
        execution_id: ID of the workflow execution to run

    Returns:
        Complete workflow execution results with insights
    """
    try:
        execution = await workflow_orchestrator.execute_workflow(
            execution_id=execution_id,
            semantic_manager=semantic_manager,
            intelligence_engine=intelligence_engine,
            statistical_tester=statistical_tester,
            conversation_memory=conversation_memory,
        )

        return {
            "execution_id": execution_id,
            "status": execution.status.value,
            "completed_steps": len(execution.completed_steps),
            "total_steps": len(execution.definition.steps),
            "failed_steps": len(execution.failed_steps),
            "execution_time_ms": execution.total_execution_time_ms,
            "insights": execution.insights,
            "results": execution.results,
            "started_at": execution.started_at,
            "completed_at": execution.completed_at,
        }

    except Exception as e:
        return {
            "error": str(e),
            "message": f"Failed to execute workflow '{execution_id}'",
        }


@mcp.tool()
async def get_workflow_status(execution_id: str) -> Dict[str, Any]:
    """
    Get current status of a workflow execution.

    Args:
        execution_id: ID of the workflow execution to check

    Returns:
        Current workflow status and progress information
    """
    try:
        status = workflow_orchestrator.get_workflow_status(execution_id)

        return {"workflow_status": status, "timestamp": datetime.now().isoformat()}

    except Exception as e:
        return {
            "error": str(e),
            "message": f"Failed to get workflow status for '{execution_id}'",
        }


@mcp.tool()
async def cancel_workflow(execution_id: str) -> Dict[str, Any]:
    """
    Cancel an active workflow execution.

    Args:
        execution_id: ID of the workflow execution to cancel

    Returns:
        Cancellation status and final workflow state
    """
    try:
        result = await workflow_orchestrator.cancel_workflow(execution_id)

        return {"cancellation_result": result, "timestamp": datetime.now().isoformat()}

    except Exception as e:
        return {
            "error": str(e),
            "message": f"Failed to cancel workflow '{execution_id}'",
        }


@mcp.tool()
async def run_conversion_analysis(
    include_cohorts: bool = True,
    include_statistical_tests: bool = True,
    custom_dimensions: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Run comprehensive conversion analysis workflow with customizable options.

    Args:
        include_cohorts: Whether to include cohort-based analysis
        include_statistical_tests: Whether to run statistical significance tests
        custom_dimensions: Additional dimensions to analyze

    Returns:
        Complete conversion analysis results with multi-dimensional insights
    """
    try:
        # Create customized workflow
        customizations = {"name": "Custom Conversion Analysis", "steps": {}}

        # Add custom dimensions if provided
        if custom_dimensions:
            customizations["steps"]["industry_breakdown"] = {
                "parameters": {
                    "dimensions": ["plan_type"] + custom_dimensions,
                    "measures": ["conversion_rate", "total_users"],
                }
            }

        # Remove steps if not requested
        if not include_cohorts:
            customizations["steps"]["cohort_analysis"] = {
                "dependencies": ["skip"]  # Mark to skip
            }

        if not include_statistical_tests:
            customizations["steps"]["statistical_validation"] = {
                "dependencies": ["skip"]  # Mark to skip
            }

        # Create and execute workflow
        execution = await workflow_orchestrator.create_workflow(
            "conversion_deep_dive", customizations
        )

        result = await workflow_orchestrator.execute_workflow(
            execution.execution_id,
            semantic_manager,
            intelligence_engine,
            statistical_tester,
            conversation_memory,
        )

        return {
            "analysis_type": "conversion_deep_dive",
            "execution_id": execution.execution_id,
            "status": result.status.value,
            "insights": result.insights,
            "key_findings": _extract_conversion_findings(result.results),
            "metadata": {
                "included_cohorts": include_cohorts,
                "included_statistical_tests": include_statistical_tests,
                "custom_dimensions": custom_dimensions or [],
                "execution_time_ms": result.total_execution_time_ms,
            },
        }

    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to run conversion analysis workflow",
        }


@mcp.tool()
async def run_feature_usage_analysis(
    focus_on_power_users: bool = True,
    include_churn_correlation: bool = True,
    feature_filter: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Run comprehensive feature usage analysis workflow.

    Args:
        focus_on_power_users: Whether to include power user analysis
        include_churn_correlation: Whether to analyze feature usage vs churn
        feature_filter: Specific features to focus on

    Returns:
        Complete feature usage analysis with engagement insights
    """
    try:
        # Create customized workflow
        customizations = {"name": "Custom Feature Usage Analysis", "steps": {}}

        # Add feature filter if provided
        if feature_filter:
            customizations["steps"]["feature_adoption"] = {
                "parameters": {"filters": {"feature_name": {"in": feature_filter}}}
            }

        # Configure optional steps
        if not focus_on_power_users:
            customizations["steps"]["power_user_analysis"] = {"dependencies": ["skip"]}

        if not include_churn_correlation:
            customizations["steps"]["churn_relationship"] = {"dependencies": ["skip"]}

        # Create and execute workflow
        execution = await workflow_orchestrator.create_workflow(
            "feature_usage_deep_dive", customizations
        )

        result = await workflow_orchestrator.execute_workflow(
            execution.execution_id,
            semantic_manager,
            intelligence_engine,
            statistical_tester,
            conversation_memory,
        )

        return {
            "analysis_type": "feature_usage_deep_dive",
            "execution_id": execution.execution_id,
            "status": result.status.value,
            "insights": result.insights,
            "feature_recommendations": _extract_feature_recommendations(result.results),
            "metadata": {
                "focused_on_power_users": focus_on_power_users,
                "included_churn_correlation": include_churn_correlation,
                "feature_filter": feature_filter or [],
                "execution_time_ms": result.total_execution_time_ms,
            },
        }

    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to run feature usage analysis workflow",
        }


def _extract_conversion_findings(results: Dict[str, Any]) -> List[str]:
    """Extract key conversion findings from workflow results"""

    findings = []

    if "baseline_conversion" in results:
        findings.append("Baseline conversion analysis completed")

    if "statistical_validation" in results:
        stat_result = results["statistical_validation"]
        if stat_result.get("test_results", {}).get("significant"):
            findings.append("Statistically significant conversion differences detected")

    if "industry_breakdown" in results:
        findings.append("Industry-based conversion patterns identified")

    return findings


def _extract_feature_recommendations(results: Dict[str, Any]) -> List[str]:
    """Extract feature recommendations from workflow results"""

    recommendations = []

    if "feature_adoption" in results:
        recommendations.append("Feature adoption patterns analyzed")

    if "usage_correlation" in results:
        correlations = (
            results["usage_correlation"]
            .get("analysis_result", {})
            .get("correlations", [])
        )
        if correlations:
            recommendations.append(
                f"Identified {len(correlations)} significant feature correlations"
            )

    if "churn_relationship" in results:
        recommendations.append("Feature usage impact on churn analyzed")

    return recommendations


# ============================================================================
# Runtime Metrics Management Tools
# ============================================================================


@mcp.tool()
async def define_custom_metric(
    name: str,
    type: str,
    model: str,
    description: str = "",
    dimension: Optional[str] = None,
    numerator: Optional[str] = None,
    denominator: Optional[str] = None,
    sql: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Define a custom metric at runtime without editing YAML files.

    This tool allows you to create ad-hoc metrics for analysis without modifying
    the semantic model configuration files. Metrics are validated against the
    semantic model and persisted to disk.

    Args:
        name: Unique metric name (e.g., "power_users", "high_value_customers")
        type: Metric type - one of:
            - "count": Count rows
            - "count_distinct": Count unique values of a dimension
            - "sum": Sum values of a dimension
            - "avg": Average values of a dimension
            - "ratio": Ratio of two metrics (requires numerator/denominator)
            - "custom_sql": Custom SQL expression (requires sql parameter)
        model: Semantic model this metric belongs to (e.g., "users", "events")
        description: Human-readable description of what this metric measures
        dimension: Column to aggregate for count_distinct, sum, or avg types
        numerator: Numerator metric name for ratio types
        denominator: Denominator metric name for ratio types
        sql: Custom SQL expression for custom_sql types
        filters: Dictionary of filters to apply (e.g., {"plan_type": "paid", "login_count__gt": 100})
        tags: List of tags for organizing metrics (e.g., ["engagement", "core"])

    Returns:
        Created metric details and status

    Examples:
        # Count distinct power users
        define_custom_metric(
            name="power_users",
            type="count_distinct",
            model="users",
            dimension="user_id",
            filters={"login_count__gt": 100},
            description="Users with 100+ logins",
            tags=["engagement"]
        )

        # Conversion rate ratio
        define_custom_metric(
            name="conversion_rate",
            type="ratio",
            model="users",
            numerator="paid_users",
            denominator="total_users",
            description="Free to paid conversion rate"
        )

        # Custom SQL calculation
        define_custom_metric(
            name="avg_revenue_per_user",
            type="custom_sql",
            model="users",
            sql="SUM(revenue) / COUNT(DISTINCT user_id)",
            description="Average revenue per user"
        )
    """
    try:
        result = await runtime_metrics_registry.define_metric(
            name=name,
            type=type,
            model=model,
            semantic_manager=semantic_manager,
            description=description,
            dimension=dimension,
            numerator=numerator,
            denominator=denominator,
            sql=sql,
            filters=filters or {},
            tags=tags or [],
        )

        return result

    except Exception as e:
        logger.error(f"Failed to define custom metric: {e}")
        return {
            "error": str(e),
            "message": "Failed to define custom metric",
            "status": "error",
        }


@mcp.tool()
async def list_custom_metrics(
    model: Optional[str] = None, tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    List all custom metrics with optional filtering.

    Returns all runtime-defined custom metrics. You can filter by semantic model
    or by tags to find specific metrics.

    Args:
        model: Filter by model name (e.g., "users", "events")
        tags: Filter by tags - returns metrics with any matching tag

    Returns:
        List of custom metrics with their definitions

    Examples:
        # List all custom metrics
        list_custom_metrics()

        # List metrics for users model
        list_custom_metrics(model="users")

        # List metrics tagged as "engagement"
        list_custom_metrics(tags=["engagement"])

        # List engagement metrics for users model
        list_custom_metrics(model="users", tags=["engagement"])
    """
    try:
        from dataclasses import asdict

        metrics = runtime_metrics_registry.list_metrics(model=model, tags=tags)

        return {
            "metrics": [asdict(m) for m in metrics],
            "total_count": len(metrics),
            "filtered_by": {
                "model": model,
                "tags": tags,
            },
            "status": "success",
        }

    except Exception as e:
        logger.error(f"Failed to list custom metrics: {e}")
        return {
            "error": str(e),
            "message": "Failed to list custom metrics",
            "status": "error",
        }


@mcp.tool()
async def delete_custom_metric(name: str) -> Dict[str, Any]:
    """
    Delete a custom metric by name.

    Removes a runtime-defined custom metric from the registry. This does not
    affect metrics defined in YAML configuration files.

    Args:
        name: Name of the metric to delete

    Returns:
        Deletion status

    Example:
        delete_custom_metric(name="temp_test_metric")
    """
    try:
        result = await runtime_metrics_registry.delete_metric(name)
        return result

    except Exception as e:
        logger.error(f"Failed to delete custom metric: {e}")
        return {
            "error": str(e),
            "message": f"Failed to delete metric '{name}'",
            "status": "error",
        }


# ============================================================================
# Server Configuration and Startup
# ============================================================================


async def initialize_semantic_layer():
    """Initialize semantic layer connections"""
    try:
        await semantic_manager.initialize()
        logger.info("Semantic layer initialized successfully")

        # Test database connection
        health = await semantic_manager.health_check()
        if health["database_connected"]:
            logger.info(f"Database connected: {health['database_info']}")
        else:
            logger.warning("Database connection failed")

        logger.info("AI Analyst MCP Server ready!")

    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        raise


# ============================================================================
# Main Entry Point
# ============================================================================


def main():
    """Main entry point for the MCP server"""
    import asyncio
    import sys

    # All startup messages go to stderr to avoid corrupting MCP STDIO protocol
    print("Starting AI Analyst MCP Server...", file=sys.stderr)
    print("Semantic Layer: Boring SL + Ibis + DuckDB", file=sys.stderr)
    print("Intelligence: Execution-first + Auto-stats + Natural language", file=sys.stderr)

    logger.info("Starting AI Analyst MCP Server")
    logger.info("Semantic Layer: Boring SL + Ibis + DuckDB")
    logger.info("Intelligence: Execution-first + Auto-stats + Natural language")

    # Initialize semantic layer before starting server
    asyncio.run(initialize_semantic_layer())

    # Run the FastMCP server
    mcp.run()


if __name__ == "__main__":
    main()
