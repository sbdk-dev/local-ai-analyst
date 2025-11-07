#!/usr/bin/env python3
"""
Query Optimization Engine for AI Analyst

Intelligent query planning, caching, batch execution, and performance optimization
based on conversation history and common analytical patterns.
"""

import time
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import json


@dataclass
class QueryExecution:
    """Represents a query execution with performance metadata"""
    query_hash: str
    sql: str
    model: str
    dimensions: List[str]
    measures: List[str]
    filters: Dict[str, Any]
    execution_time_ms: float
    row_count: int
    timestamp: str
    cache_hit: bool = False


@dataclass
class QueryBatch:
    """Represents a batch of related queries that can be optimized together"""
    batch_id: str
    queries: List[Dict[str, Any]]
    shared_dimensions: List[str]
    shared_filters: Dict[str, Any]
    estimated_time_ms: float
    optimization_type: str


class QueryCache:
    """Intelligent query result cache with TTL and invalidation"""

    def __init__(self, max_size: int = 1000, default_ttl_minutes: int = 30):
        self.max_size = max_size
        self.default_ttl = timedelta(minutes=default_ttl_minutes)
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, datetime] = {}
        self.ttl_overrides: Dict[str, timedelta] = {}

    def _generate_cache_key(self, query_info: Dict[str, Any]) -> str:
        """Generate consistent cache key for query"""
        key_data = {
            "model": query_info.get("model", ""),
            "dimensions": sorted(query_info.get("dimensions", [])),
            "measures": sorted(query_info.get("measures", [])),
            "filters": json.dumps(query_info.get("filters", {}), sort_keys=True)
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, query_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Retrieve cached result if valid"""
        cache_key = self._generate_cache_key(query_info)

        if cache_key not in self.cache:
            return None

        # Check TTL
        cached_time = self.access_times[cache_key]
        ttl = self.ttl_overrides.get(cache_key, self.default_ttl)

        if datetime.now() - cached_time > ttl:
            # Expired, remove from cache
            del self.cache[cache_key]
            del self.access_times[cache_key]
            if cache_key in self.ttl_overrides:
                del self.ttl_overrides[cache_key]
            return None

        # Update access time
        self.access_times[cache_key] = datetime.now()

        # Mark as cache hit
        result = self.cache[cache_key].copy()
        result["metadata"] = result.get("metadata", {})
        result["metadata"]["cache_hit"] = True
        result["metadata"]["cached_at"] = cached_time.isoformat()

        return result

    def put(self, query_info: Dict[str, Any], result: Dict[str, Any], ttl_minutes: Optional[int] = None):
        """Store query result in cache"""
        cache_key = self._generate_cache_key(query_info)

        # Clean cache if at capacity
        if len(self.cache) >= self.max_size:
            self._evict_oldest()

        # Store result
        self.cache[cache_key] = result.copy()
        self.access_times[cache_key] = datetime.now()

        # Set custom TTL if specified
        if ttl_minutes:
            self.ttl_overrides[cache_key] = timedelta(minutes=ttl_minutes)

    def invalidate_model(self, model: str):
        """Invalidate all cached results for a specific model"""
        keys_to_remove = []
        for cache_key, result in self.cache.items():
            if result.get("metadata", {}).get("model") == model:
                keys_to_remove.append(cache_key)

        for key in keys_to_remove:
            if key in self.cache:
                del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
            if key in self.ttl_overrides:
                del self.ttl_overrides[key]

    def clear(self):
        """Clear all cached results"""
        self.cache.clear()
        self.access_times.clear()
        self.ttl_overrides.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "oldest_entry": min(self.access_times.values()).isoformat() if self.access_times else None,
            "newest_entry": max(self.access_times.values()).isoformat() if self.access_times else None
        }

    def _evict_oldest(self):
        """Remove oldest cache entry"""
        if not self.access_times:
            return

        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        del self.cache[oldest_key]
        del self.access_times[oldest_key]
        if oldest_key in self.ttl_overrides:
            del self.ttl_overrides[oldest_key]


class QueryOptimizer:
    """Advanced query optimization engine"""

    def __init__(self, cache_size: int = 1000, cache_ttl_minutes: int = 30):
        self.cache = QueryCache(cache_size, cache_ttl_minutes)
        self.execution_history: List[QueryExecution] = []
        self.performance_baselines: Dict[str, float] = {}
        self.common_patterns: Dict[str, int] = Counter()
        self.batch_opportunities: List[QueryBatch] = []

    async def optimize_query(
        self,
        query_info: Dict[str, Any],
        conversation_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Optimize a query based on cache, patterns, and conversation context
        """

        optimization_result = {
            "original_query": query_info.copy(),
            "optimizations_applied": [],
            "estimated_performance": {},
            "cache_recommendation": None,
            "batch_opportunities": []
        }

        # 1. Check cache first
        cached_result = self.cache.get(query_info)
        if cached_result:
            optimization_result["cache_recommendation"] = "cache_hit"
            optimization_result["optimizations_applied"].append("cache_hit")
            return {
                "optimized_query": query_info,
                "optimization_result": optimization_result,
                "cached_result": cached_result
            }

        # 2. Analyze query complexity
        complexity_analysis = self._analyze_complexity(query_info)
        optimization_result["estimated_performance"] = complexity_analysis

        # 3. Check for dimension/measure optimization opportunities
        optimized_query = await self._optimize_dimensions_measures(query_info, conversation_context)
        if optimized_query != query_info:
            optimization_result["optimizations_applied"].append("dimension_measure_optimization")

        # 4. Check for filter optimization
        filter_optimized = self._optimize_filters(optimized_query)
        if filter_optimized != optimized_query:
            optimization_result["optimizations_applied"].append("filter_optimization")
            optimized_query = filter_optimized

        # 5. Identify batch opportunities
        batch_ops = await self._identify_batch_opportunities(optimized_query, conversation_context)
        if batch_ops:
            optimization_result["batch_opportunities"] = batch_ops
            optimization_result["optimizations_applied"].append("batch_identified")

        # 6. Set cache TTL recommendation
        cache_ttl = self._recommend_cache_ttl(optimized_query, complexity_analysis)
        optimization_result["cache_recommendation"] = {
            "ttl_minutes": cache_ttl,
            "reason": self._get_cache_reason(optimized_query, complexity_analysis)
        }

        return {
            "optimized_query": optimized_query,
            "optimization_result": optimization_result
        }

    async def execute_with_optimization(
        self,
        query_info: Dict[str, Any],
        executor_func,
        conversation_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute query with full optimization pipeline
        """

        start_time = time.time()

        # 1. Optimize the query
        optimization = await self.optimize_query(query_info, conversation_context)
        optimized_query = optimization["optimized_query"]
        optimization_result = optimization["optimization_result"]

        # 2. Check if we have a cached result
        if "cached_result" in optimization:
            cached_result = optimization["cached_result"]
            cached_result["optimization_metadata"] = optimization_result
            return cached_result

        # 3. Execute the optimized query
        result = await executor_func(optimized_query)

        # 4. Record execution for learning
        execution_time = (time.time() - start_time) * 1000
        await self._record_execution(optimized_query, result, execution_time)

        # 5. Cache the result
        cache_ttl = optimization_result.get("cache_recommendation", {}).get("ttl_minutes", 30)
        self.cache.put(optimized_query, result, cache_ttl)

        # 6. Add optimization metadata
        result["optimization_metadata"] = optimization_result

        return result

    async def suggest_batch_execution(
        self,
        pending_queries: List[Dict[str, Any]]
    ) -> List[QueryBatch]:
        """
        Analyze pending queries and suggest optimal batching strategies
        """

        batches = []

        # Group queries by model
        by_model = defaultdict(list)
        for query in pending_queries:
            by_model[query.get("model", "")].append(query)

        for model, queries in by_model.items():
            if len(queries) < 2:
                continue

            # Find shared dimensions
            shared_dims = self._find_shared_dimensions(queries)
            shared_filters = self._find_shared_filters(queries)

            if shared_dims or shared_filters:
                batch = QueryBatch(
                    batch_id=f"batch_{model}_{len(batches)}",
                    queries=queries,
                    shared_dimensions=shared_dims,
                    shared_filters=shared_filters,
                    estimated_time_ms=self._estimate_batch_time(queries),
                    optimization_type="shared_dimensions" if shared_dims else "shared_filters"
                )
                batches.append(batch)

        return batches

    async def get_performance_insights(self) -> Dict[str, Any]:
        """
        Analyze performance patterns and provide optimization insights
        """

        if not self.execution_history:
            return {"status": "insufficient_data"}

        recent_executions = [e for e in self.execution_history[-100:]]  # Last 100 executions

        # Performance by model
        by_model = defaultdict(list)
        for execution in recent_executions:
            by_model[execution.model].append(execution.execution_time_ms)

        model_performance = {}
        for model, times in by_model.items():
            model_performance[model] = {
                "avg_time_ms": sum(times) / len(times),
                "min_time_ms": min(times),
                "max_time_ms": max(times),
                "execution_count": len(times)
            }

        # Cache hit rate
        cache_hits = sum(1 for e in recent_executions if e.cache_hit)
        cache_hit_rate = cache_hits / len(recent_executions) if recent_executions else 0

        # Common patterns
        dimension_patterns = Counter()
        measure_patterns = Counter()
        for execution in recent_executions:
            if len(execution.dimensions) > 1:
                dimension_patterns[tuple(sorted(execution.dimensions))] += 1
            if len(execution.measures) > 1:
                measure_patterns[tuple(sorted(execution.measures))] += 1

        return {
            "performance_summary": {
                "total_executions": len(recent_executions),
                "avg_execution_time_ms": sum(e.execution_time_ms for e in recent_executions) / len(recent_executions),
                "cache_hit_rate": cache_hit_rate
            },
            "model_performance": model_performance,
            "cache_stats": self.cache.get_stats(),
            "common_patterns": {
                "dimension_combinations": dict(dimension_patterns.most_common(5)),
                "measure_combinations": dict(measure_patterns.most_common(5))
            },
            "optimization_opportunities": self._identify_optimization_opportunities(recent_executions)
        }

    # Private helper methods

    def _analyze_complexity(self, query_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze query complexity for performance estimation"""

        dimensions = query_info.get("dimensions", [])
        measures = query_info.get("measures", [])
        filters = query_info.get("filters", {})

        # Complexity scoring
        complexity_score = 0
        complexity_score += len(dimensions) * 2  # Each dimension adds complexity
        complexity_score += len(measures) * 1.5  # Each measure adds complexity
        complexity_score += len(filters) * 1     # Each filter adds some complexity

        # Special complexity cases
        if len(dimensions) > 3:
            complexity_score += 5  # High-cardinality grouping

        # Estimate based on historical data
        similar_queries = [
            e for e in self.execution_history[-50:]
            if e.model == query_info.get("model", "") and
            len(e.dimensions) == len(dimensions) and
            len(e.measures) == len(measures)
        ]

        estimated_time = 100  # Default estimate
        if similar_queries:
            estimated_time = sum(e.execution_time_ms for e in similar_queries) / len(similar_queries)

        return {
            "complexity_score": complexity_score,
            "estimated_time_ms": estimated_time,
            "complexity_level": "low" if complexity_score < 5 else "medium" if complexity_score < 10 else "high",
            "similar_query_count": len(similar_queries)
        }

    async def _optimize_dimensions_measures(
        self,
        query_info: Dict[str, Any],
        conversation_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Optimize dimensions and measures based on conversation patterns"""

        optimized = query_info.copy()

        if not conversation_context:
            return optimized

        # Get frequently used dimensions with current measures
        current_measures = set(query_info.get("measures", []))
        frequently_paired_dims = []

        # Analyze conversation context for common dimension patterns
        explored_dims = conversation_context.get("dimensions_explored", [])
        if explored_dims and len(explored_dims) > len(query_info.get("dimensions", [])):
            # Suggest adding dimensions that are commonly used
            dimension_usage = Counter(explored_dims)
            current_dims = set(query_info.get("dimensions", []))

            for dim, count in dimension_usage.most_common(3):
                if dim not in current_dims and count > 1:
                    frequently_paired_dims.append(dim)

        if frequently_paired_dims:
            optimized.setdefault("suggested_additions", {})["dimensions"] = frequently_paired_dims[:2]

        return optimized

    def _optimize_filters(self, query_info: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize filter conditions for better performance"""

        optimized = query_info.copy()
        filters = query_info.get("filters", {})

        if not filters:
            return optimized

        # Reorder filters for optimal execution (most selective first)
        # This is a simplified heuristic - in practice would analyze data distribution
        filter_selectivity = {}
        for key, value in filters.items():
            if isinstance(value, list):
                filter_selectivity[key] = len(value)  # More values = less selective
            else:
                filter_selectivity[key] = 1

        # Sort by selectivity (lower score = more selective = should go first)
        sorted_filters = dict(sorted(filters.items(), key=lambda x: filter_selectivity[x[0]]))

        if sorted_filters != filters:
            optimized["filters"] = sorted_filters

        return optimized

    async def _identify_batch_opportunities(
        self,
        query_info: Dict[str, Any],
        conversation_context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify opportunities to batch this query with likely follow-ups"""

        opportunities = []

        if not conversation_context:
            return opportunities

        model = query_info.get("model", "")
        dimensions = query_info.get("dimensions", [])
        measures = query_info.get("measures", [])

        # Based on conversation patterns, suggest likely next queries
        conversation_themes = conversation_context.get("conversation_themes", [])

        # If analyzing by plan_type, likely to also want industry analysis
        if "plan_type" in dimensions and "plan_type_segmentation" in conversation_themes:
            opportunities.append({
                "type": "dimensional_expansion",
                "suggested_query": {
                    "model": model,
                    "dimensions": dimensions + ["industry"],
                    "measures": measures
                },
                "reason": "Common pattern: plan_type analysis followed by industry breakdown"
            })

        # If looking at conversion_rate, likely to want statistical testing
        if "conversion_rate" in measures and len(dimensions) > 0:
            opportunities.append({
                "type": "statistical_validation",
                "suggested_query": {
                    "model": "statistical_test",
                    "dimensions": dimensions,
                    "measures": measures
                },
                "reason": "Pattern: conversion analysis typically followed by significance testing"
            })

        return opportunities

    def _recommend_cache_ttl(self, query_info: Dict[str, Any], complexity: Dict[str, Any]) -> int:
        """Recommend cache TTL based on query characteristics"""

        # Base TTL
        ttl_minutes = 30

        # Adjust based on complexity
        if complexity["complexity_level"] == "high":
            ttl_minutes = 60  # Cache expensive queries longer
        elif complexity["complexity_level"] == "low":
            ttl_minutes = 15  # Simple queries don't need long caching

        # Adjust based on data volatility (simplified heuristic)
        model = query_info.get("model", "")
        if "events" in model.lower():
            ttl_minutes = min(ttl_minutes, 10)  # Event data changes frequently
        elif "users" in model.lower():
            ttl_minutes = max(ttl_minutes, 45)  # User data is more stable

        return ttl_minutes

    def _get_cache_reason(self, query_info: Dict[str, Any], complexity: Dict[str, Any]) -> str:
        """Explain cache TTL reasoning"""

        reasons = []

        if complexity["complexity_level"] == "high":
            reasons.append("High complexity query - longer cache duration")

        model = query_info.get("model", "")
        if "events" in model.lower():
            reasons.append("Event data changes frequently - shorter cache duration")
        elif "users" in model.lower():
            reasons.append("User data is relatively stable - longer cache duration")

        return "; ".join(reasons) if reasons else "Standard cache duration"

    async def _record_execution(
        self,
        query_info: Dict[str, Any],
        result: Dict[str, Any],
        execution_time_ms: float
    ):
        """Record query execution for performance learning"""

        query_hash = hashlib.md5(
            json.dumps(query_info, sort_keys=True).encode()
        ).hexdigest()

        execution = QueryExecution(
            query_hash=query_hash,
            sql=query_info.get("sql", ""),
            model=query_info.get("model", ""),
            dimensions=query_info.get("dimensions", []),
            measures=query_info.get("measures", []),
            filters=query_info.get("filters", {}),
            execution_time_ms=execution_time_ms,
            row_count=result.get("row_count", 0),
            timestamp=datetime.now().isoformat(),
            cache_hit=False
        )

        self.execution_history.append(execution)

        # Keep only recent executions
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-500:]

    def _find_shared_dimensions(self, queries: List[Dict[str, Any]]) -> List[str]:
        """Find dimensions common across multiple queries"""
        if len(queries) < 2:
            return []

        shared = set(queries[0].get("dimensions", []))
        for query in queries[1:]:
            shared &= set(query.get("dimensions", []))

        return list(shared)

    def _find_shared_filters(self, queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find filters common across multiple queries"""
        if len(queries) < 2:
            return {}

        shared_filters = {}
        first_filters = queries[0].get("filters", {})

        for key, value in first_filters.items():
            if all(query.get("filters", {}).get(key) == value for query in queries[1:]):
                shared_filters[key] = value

        return shared_filters

    def _estimate_batch_time(self, queries: List[Dict[str, Any]]) -> float:
        """Estimate execution time for batch of queries"""
        # Simplified estimation - in practice would be more sophisticated
        individual_estimates = []
        for query in queries:
            complexity = self._analyze_complexity(query)
            individual_estimates.append(complexity["estimated_time_ms"])

        # Assume 20% efficiency gain from batching
        total_individual = sum(individual_estimates)
        return total_individual * 0.8

    def _identify_optimization_opportunities(self, executions: List[QueryExecution]) -> List[Dict[str, Any]]:
        """Identify specific optimization opportunities from execution history"""
        opportunities = []

        # Check for repeated expensive queries (cache misses)
        expensive_queries = [e for e in executions if e.execution_time_ms > 200 and not e.cache_hit]
        if len(expensive_queries) > 3:
            opportunities.append({
                "type": "cache_optimization",
                "description": f"{len(expensive_queries)} expensive queries could benefit from longer cache TTL",
                "impact": "high"
            })

        # Check for redundant dimension patterns
        dimension_combos = Counter(tuple(sorted(e.dimensions)) for e in executions if len(e.dimensions) > 1)
        frequent_combos = [combo for combo, count in dimension_combos.items() if count > 5]
        if frequent_combos:
            opportunities.append({
                "type": "precomputation",
                "description": f"Common dimension combinations: {frequent_combos[:2]} could be precomputed",
                "impact": "medium"
            })

        return opportunities