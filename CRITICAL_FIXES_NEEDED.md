# AI Analyst System - Critical Fixes Required

## Fix Priority: CRITICAL (Must complete before any deployment)

---

## FIX #1: MCP Server Method References (Lines 940, 1016)

### Problem
```python
# Current broken code in server.py:
@mcp.tool()
async def run_conversion_analysis(...):
    ...
    "key_findings": self._extract_conversion_findings(result.results),  # ❌ FAILS
    
@mcp.tool()
async def run_feature_usage_analysis(...):
    ...
    "feature_recommendations": self._extract_feature_recommendations(result.results),  # ❌ FAILS

# At module level (lines 1031-1065):
def _extract_conversion_findings(results: Dict[str, Any]) -> List[str]:  # Not a method!
    ...
    
def _extract_feature_recommendations(results: Dict[str, Any]) -> List[str]:  # Not a method!
    ...
```

### Solution

**Option A: Make them module-level helper calls (Recommended)**
```python
# Fix the tool calls:
@mcp.tool()
async def run_conversion_analysis(...):
    ...
    # Use module-level function directly:
    "key_findings": _extract_conversion_findings(result.results),  # ✅ WORKS
    
@mcp.tool()
async def run_feature_usage_analysis(...):
    ...
    # Use module-level function directly:
    "feature_recommendations": _extract_feature_recommendations(result.results),  # ✅ WORKS
```

**Option B: Create a helper class**
```python
class WorkflowResultExtractor:
    @staticmethod
    def extract_conversion_findings(results: Dict[str, Any]) -> List[str]:
        ...
    
    @staticmethod
    def extract_feature_recommendations(results: Dict[str, Any]) -> List[str]:
        ...

# Then in tools:
extractor = WorkflowResultExtractor()
"key_findings": extractor.extract_conversion_findings(result.results),  # ✅ WORKS
"feature_recommendations": extractor.extract_feature_recommendations(result.results),  # ✅ WORKS
```

**Effort**: 30 minutes  
**Testing**: Run `test_phase_4_3_workflows.py` to verify

---

## FIX #2: QueryOptimizer Missing Methods (Lines 147-161, 203, 235, etc.)

### Problem
```python
# Current broken code in server.py lines 147-161:
query_key = query_optimizer.generate_cache_key(query_info)          # ❌ No such method
cached_result = query_optimizer.get_cached_result(query_key)        # ❌ No such method
result["cache_hit"] = True
result["cache_timestamp"] = cached_result.get("cache_timestamp")

# ... and 10+ other undefined method calls throughout server.py
```

### Solution

**Create adapter methods in QueryOptimizer or server:**

```python
# Add these methods to QueryOptimizer class:
class QueryOptimizer:
    def generate_cache_key(self, query_info: Dict[str, Any]) -> str:
        """Generate cache key from query info"""
        return self.cache._generate_cache_key(query_info)
    
    def get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get result from cache"""
        # Need to refactor to support key-based lookup
        # Or better: implement proper query lookup
        if cache_key in self.cache.cache:
            self.cache.access_times[cache_key] = datetime.now()
            return self.cache.cache[cache_key].copy()
        return None
    
    def cache_result(self, query_key: str, result: Dict[str, Any], query_info: Dict[str, Any]):
        """Cache a query result"""
        cache_ttl = self._recommend_cache_ttl(query_info, self._analyze_complexity(query_info))
        self.cache.put(query_info, result, cache_ttl)
    
    def analyze_query_complexity(self, query_info: Dict[str, Any]) -> Dict[str, Any]:
        """Public wrapper for complexity analysis"""
        return self._analyze_complexity(query_info)
    
    def get_optimization_insights(self, query_info: Dict[str, Any], result: Dict[str, Any], conversation_memory) -> List[str]:
        """Extract optimization insights"""
        insights = []
        complexity = self._analyze_complexity(query_info)
        
        if complexity["complexity_level"] == "high":
            if self.cache.get(query_info) is None:
                insights.append("Consider caching this complex query")
        
        if result.get("row_count", 0) > 10000:
            insights.append("Large result set - consider adding filters")
        
        return insights
    
    def get_cache_hit_rate(self) -> float:
        """Calculate current cache hit rate"""
        if not self.execution_history:
            return 0.0
        cache_hits = sum(1 for e in self.execution_history if e.cache_hit)
        return cache_hits / len(self.execution_history) if self.execution_history else 0.0
    
    def get_oldest_cache_entry(self) -> Optional[str]:
        """Get timestamp of oldest cache entry"""
        if not self.cache.access_times:
            return None
        return min(self.cache.access_times.values()).isoformat()
    
    def get_newest_cache_entry(self) -> Optional[str]:
        """Get timestamp of newest cache entry"""
        if not self.cache.access_times:
            return None
        return max(self.cache.access_times.values()).isoformat()
    
    def get_cache_memory_usage(self) -> Dict[str, Any]:
        """Estimate cache memory usage"""
        import sys
        total_size = sum(sys.getsizeof(v) for v in self.cache.cache.values())
        return {
            "entries": len(self.cache.cache),
            "estimated_bytes": total_size,
            "estimated_mb": total_size / (1024 * 1024)
        }
    
    def get_optimization_patterns(self, conversation_memory) -> List[Dict[str, Any]]:
        """Extract optimization patterns"""
        if not self.execution_history:
            return []
        
        patterns = []
        
        # Identify frequently cached queries
        cache_hits = [e for e in self.execution_history if e.cache_hit]
        if cache_hits:
            patterns.append({
                "type": "cache_effectiveness",
                "hit_rate": len(cache_hits) / len(self.execution_history),
                "recommendation": "High cache effectiveness - maintain current TTL"
            })
        
        return patterns
    
    def get_performance_trends(self, conversation_memory) -> List[Dict[str, Any]]:
        """Analyze performance trends"""
        if not self.execution_history:
            return []
        
        trends = []
        recent = self.execution_history[-50:]  # Last 50 executions
        
        avg_time = sum(e.execution_time_ms for e in recent) / len(recent) if recent else 0
        
        trends.append({
            "metric": "average_query_time",
            "value": avg_time,
            "unit": "ms",
            "period": "last_50_queries"
        })
        
        return trends
    
    def get_high_impact_optimizations(self, conversation_memory) -> List[Dict[str, Any]]:
        """Get high-impact optimization opportunities"""
        opportunities = []
        
        # Identify slow queries
        slow_queries = [e for e in self.execution_history if e.execution_time_ms > 500]
        if len(slow_queries) > 3:
            opportunities.append({
                "type": "slow_queries",
                "count": len(slow_queries),
                "recommendation": "Add filters or caching to slow queries",
                "impact": "high"
            })
        
        return opportunities
    
    def get_quick_optimization_wins(self, conversation_memory) -> List[Dict[str, Any]]:
        """Get quick wins for optimization"""
        wins = []
        
        # Identify repeated queries that could be cached
        query_counts = {}
        for e in self.execution_history:
            query_counts[e.query_hash] = query_counts.get(e.query_hash, 0) + 1
        
        repeated = [q for q, count in query_counts.items() if count > 5]
        if repeated:
            wins.append({
                "type": "cache_repeated",
                "count": len(repeated),
                "recommendation": "Enable caching for repeated queries",
                "impact": "quick"
            })
        
        return wins
    
    def get_cache_tuning_recommendations(self) -> List[Dict[str, Any]]:
        """Get cache tuning recommendations"""
        recommendations = []
        
        cache_utilization = len(self.cache.cache) / self.cache.max_size
        
        if cache_utilization > 0.8:
            recommendations.append({
                "parameter": "cache_size",
                "current_value": self.cache.max_size,
                "recommendation": "Increase cache size - currently 80% full",
                "suggested_value": self.cache.max_size * 1.5
            })
        
        return recommendations
    
    def identify_batch_opportunities(self, query_info: Dict[str, Any], conversation_memory) -> List[Dict[str, Any]]:
        """Identify queries that could be batched"""
        opportunities = []
        
        # Look for similar queries in recent history
        model = query_info.get("model", "")
        dimensions = set(query_info.get("dimensions", []))
        
        similar = []
        for e in self.execution_history[-20:]:
            if e.model == model and len(set(e.dimensions) & dimensions) > 0:
                similar.append(e)
        
        if len(similar) > 2:
            opportunities.append({
                "type": "similar_dimensions",
                "count": len(similar),
                "recommendation": "Consider batching queries with similar dimensions"
            })
        
        return opportunities
    
    def get_optimization_suggestions(self, query_info: Dict[str, Any], conversation_memory) -> List[str]:
        """Get optimization suggestions for a specific query"""
        suggestions = []
        
        complexity = self._analyze_complexity(query_info)
        if complexity["complexity_level"] == "high":
            suggestions.append("This is a complex query - ensure it's cached")
        
        if len(query_info.get("filters", {})) == 0:
            suggestions.append("Consider adding filters to reduce result set")
        
        return suggestions
```

**Effort**: 2-3 hours  
**Testing**: Run `test_mcp_server.py` with actual cache operations

---

## FIX #3: Conversation Memory Helper Methods

### Problem
```python
# Lines 158-173 call these but they don't exist:
def suggest_contextual_next_steps(self, current_result: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
    suggestions = []
    context = self.get_conversation_context()
    
    if context.get("status") == "no_recent_context":
        return self._get_starter_suggestions()  # ❌ MISSING
    
    current_focus = context.get("current_analytical_focus", {})
    recent_themes = context.get("conversation_themes", [])
    
    if current_focus:
        suggestions.extend(self._suggest_deepening_analysis(current_focus))  # ❌ MISSING
    
    if recent_themes:
        suggestions.extend(self._suggest_expanding_scope(recent_themes))  # ❌ MISSING
    
    for pattern in self.discovered_patterns[-3:]:
        suggestions.extend(self._suggest_pattern_followup(pattern))  # ❌ MISSING
    
    suggestions.extend(self._suggest_statistical_validation())  # ❌ MISSING
    suggestions.extend(self._suggest_temporal_analysis())  # ❌ MISSING
    
    unique_suggestions = self._deduplicate_suggestions(suggestions)  # ❌ MISSING
```

### Solution

```python
def _get_starter_suggestions(self) -> List[Dict[str, str]]:
    """Get suggestions for starting fresh analysis"""
    return [
        {
            "question": "How many users do we have overall?",
            "reasoning": "Start with basic user metrics",
            "model": "users",
            "priority": "high"
        },
        {
            "question": "What's the distribution of users by plan type?",
            "reasoning": "Understand user segments",
            "model": "users",
            "priority": "high"
        },
        {
            "question": "What are the most popular features?",
            "reasoning": "Identify key product usage",
            "model": "events",
            "priority": "medium"
        }
    ]

def _suggest_deepening_analysis(self, current_focus: Dict[str, Any]) -> List[Dict[str, str]]:
    """Suggest ways to deepen current analysis"""
    suggestions = []
    
    focus_area = current_focus.get("area", "")
    
    if "conversion" in focus_area.lower():
        suggestions.append({
            "question": f"How does conversion vary by {focus_area}?",
            "reasoning": "Deepen current conversion analysis",
            "priority": "high"
        })
        suggestions.append({
            "question": f"What's the statistical significance of conversion differences by {focus_area}?",
            "reasoning": "Add statistical rigor to findings",
            "priority": "high"
        })
    
    if "engagement" in focus_area.lower():
        suggestions.append({
            "question": "How have engagement levels trended over time?",
            "reasoning": "Understand engagement trajectory",
            "priority": "medium"
        })
    
    return suggestions

def _suggest_expanding_scope(self, recent_themes: List[str]) -> List[Dict[str, str]]:
    """Suggest ways to expand analysis scope"""
    suggestions = []
    
    # If analyzing one dimension, suggest related dimensions
    if recent_themes:
        if "plan_type" in str(recent_themes):
            suggestions.append({
                "question": "How do these patterns differ across industries?",
                "reasoning": "Expand to another segmentation dimension",
                "priority": "medium"
            })
        
        if "industry" in str(recent_themes):
            suggestions.append({
                "question": "How do these patterns vary by plan type?",
                "reasoning": "Cross-segment analysis",
                "priority": "medium"
            })
    
    return suggestions

def _suggest_pattern_followup(self, pattern: Dict[str, Any]) -> List[Dict[str, str]]:
    """Suggest follow-ups to discovered patterns"""
    suggestions = []
    pattern_type = pattern.get("type", "")
    
    if pattern_type == "dimension_combination":
        dimension_combo = pattern.get("pattern", [])
        suggestions.append({
            "question": f"Why do {' and '.join(dimension_combo)} correlate?",
            "reasoning": "Understand the drivers of observed pattern",
            "priority": "high"
        })
    
    return suggestions

def _suggest_statistical_validation(self) -> List[Dict[str, str]]:
    """Suggest statistical tests to validate findings"""
    suggestions = []
    
    # Look at recent interactions
    if len(self.interactions) > 0:
        recent = self.interactions[-1]
        
        if len(recent.dimensions) > 1 and recent.result_summary.get("row_count", 0) > 1:
            suggestions.append({
                "question": f"Are the differences in {recent.measures[0] if recent.measures else 'metrics'} statistically significant?",
                "reasoning": "Validate findings with statistical tests",
                "priority": "medium"
            })
    
    return suggestions

def _suggest_temporal_analysis(self) -> List[Dict[str, str]]:
    """Suggest time-based analyses"""
    suggestions = []
    
    # Suggest temporal analysis if not recently done
    has_temporal = any("time" in str(i.measures).lower() or "date" in str(i.dimensions).lower() 
                      for i in self.interactions[-10:])
    
    if not has_temporal:
        suggestions.append({
            "question": "How have metrics trended over time?",
            "reasoning": "Understand temporal patterns",
            "priority": "medium"
        })
    
    return suggestions

def _deduplicate_suggestions(self, suggestions: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Remove duplicate suggestions and rank by priority"""
    seen = set()
    unique = []
    
    for suggestion in suggestions:
        question = suggestion.get("question", "")
        if question not in seen:
            seen.add(question)
            unique.append(suggestion)
    
    # Sort by priority (high -> medium -> low)
    priority_order = {"high": 0, "medium": 1, "low": 2}
    unique.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 3))
    
    return unique

# Also implement missing methods referenced in existing code:
def _extract_conversation_themes(self, interactions: List[AnalysisInteraction]) -> List[str]:
    """Extract themes from conversation"""
    themes = []
    
    # Analyze models used
    models = [i.model_used for i in interactions]
    if len(set(models)) > 0:
        themes.append(f"Analyzing {', '.join(set(models))}")
    
    # Analyze dimensions
    all_dims = [d for i in interactions for d in i.dimensions]
    if all_dims:
        common_dims = Counter(all_dims).most_common(2)
        themes.append(f"Focus on {', '.join([d for d, _ in common_dims])}")
    
    return themes[:3]  # Top 3 themes

def _identify_current_focus(self, interactions: List[AnalysisInteraction]) -> Dict[str, Any]:
    """Identify current analytical focus"""
    if not interactions:
        return {}
    
    recent = interactions[-1]
    
    return {
        "area": recent.model_used,
        "dimensions": recent.dimensions,
        "measures": recent.measures,
        "last_interaction": recent.timestamp
    }

def _analyze_question_evolution(self, interactions: List[AnalysisInteraction]) -> List[str]:
    """Track how questions have evolved"""
    evolution = []
    
    for i, interaction in enumerate(interactions[-5:]):
        evolution.append(f"{i+1}. {interaction.user_question[:50]}...")
    
    return evolution

def _update_usage_patterns(self, interaction: AnalysisInteraction):
    """Update usage statistics"""
    self.model_usage[interaction.model_used] += 1
    for dim in interaction.dimensions:
        self.dimension_usage[dim] += 1
    for measure in interaction.measures:
        self.measure_usage[measure] += 1

def _update_user_interests(self, interaction: AnalysisInteraction):
    """Update user interest tracking"""
    for dim in interaction.dimensions:
        if dim not in self.user_interests:
            self.user_interests[dim] = UserInterest(
                topic=dim,
                frequency=1,
                last_accessed=interaction.timestamp,
                related_dimensions=set(interaction.dimensions),
                related_measures=set(interaction.measures),
                typical_filters=interaction.filters
            )
        else:
            self.user_interests[dim].frequency += 1
            self.user_interests[dim].last_accessed = interaction.timestamp

def _cleanup_old_interactions(self):
    """Remove interactions outside context window"""
    cutoff_time = datetime.now() - timedelta(hours=self.context_window_hours)
    self.interactions = [
        i for i in self.interactions
        if datetime.fromisoformat(i.timestamp) > cutoff_time
    ]

def _summarize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
    """Create summary of query result"""
    return {
        "row_count": result.get("row_count", 0),
        "column_count": result.get("column_count", 0),
        "execution_time_ms": result.get("execution_time_ms", 0)
    }

def _generate_interaction_id(self, question: str, query_info: Dict[str, Any]) -> str:
    """Generate unique interaction ID"""
    import hashlib
    key = f"{question}_{query_info.get('model', '')}_{int(time.time())}"
    return hashlib.md5(key.encode()).hexdigest()[:12]

def export_conversation_summary(self) -> Dict[str, Any]:
    """Export conversation summary"""
    return {
        "total_interactions": len(self.interactions),
        "models_used": dict(self.model_usage.most_common(10)),
        "dimensions_explored": dict(self.dimension_usage.most_common(10)),
        "measures_analyzed": dict(self.measure_usage.most_common(10)),
        "discovered_patterns": self.discovered_patterns,
        "user_interests": {k: v.topic for k, v in self.user_interests.items()}
    }

def get_query_recommendations(self, query_info: Dict[str, Any]) -> Dict[str, Any]:
    """Get recommendations for a potential query"""
    model = query_info.get("model", "")
    dimensions = query_info.get("dimensions", [])
    
    return {
        "model": model,
        "additional_dimensions": list(set(d for i in self.interactions 
                                         if i.model_used == model for d in i.dimensions)),
        "additional_measures": list(set(m for i in self.interactions 
                                       if i.model_used == model for m in i.measures)),
        "performance_notes": [],
        "alternative_approaches": []
    }

def get_query_usage_patterns(self) -> Dict[str, Any]:
    """Get query usage patterns"""
    return dict(self.model_usage.most_common(10))

def get_model_usage_stats(self) -> Dict[str, Any]:
    """Get model usage statistics"""
    return {model: count for model, count in self.model_usage.most_common()}

def get_popular_dimension_combinations(self) -> List[List[str]]:
    """Get popular dimension combinations"""
    combos = Counter()
    for interaction in self.interactions:
        if len(interaction.dimensions) > 1:
            combo = tuple(sorted(interaction.dimensions))
            combos[combo] += 1
    
    return [list(combo) for combo, _ in combos.most_common(5)]
```

**Effort**: 3-4 hours  
**Testing**: Run `test_conversation_memory.py`

---

## FIX #4: Workflow Analysis Mock Implementations

### Problem
```python
# Lines 751-844 all return hardcoded mock data:
async def _perform_correlation_analysis(...) -> Dict[str, Any]:
    # Returns hardcoded correlations
    correlations = []
    correlations.append({
        "feature_pair": ["dashboard_view", "report_create"],
        "correlation": 0.72,  # ❌ HARDCODED
        "significance": "high"
    })

async def _perform_expansion_analysis(...) -> Dict[str, Any]:
    # Returns hardcoded opportunities
    opportunities.append({
        "segment": "basic_plan_high_usage",
        "expansion_potential": "high",
        "estimated_additional_mrr": 15000,  # ❌ HARDCODED
        "confidence": 0.85
    })
```

### Solution

At minimum, implement basic logic instead of pure mocks:

```python
async def _perform_correlation_analysis(
    self,
    analysis_data: Dict[str, Any],
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """Perform correlation analysis on features"""
    
    correlations = []
    
    # Extract data from dependencies
    feature_data = {}
    for dep_id, dep_result in analysis_data.items():
        if "data" in dep_result:
            for row in dep_result["data"]:
                if "feature_name" in row:
                    feature = row["feature_name"]
                    if feature not in feature_data:
                        feature_data[feature] = []
                    feature_data[feature].append(row)
    
    # Calculate real correlations if we have numeric data
    if len(feature_data) > 1:
        features = list(feature_data.keys())
        
        for i, feat1 in enumerate(features):
            for feat2 in features[i+1:]:
                # Get usage counts
                count1 = sum(1 for _ in feature_data[feat1])
                count2 = sum(1 for _ in feature_data[feat2])
                
                if count1 > 0 and count2 > 0:
                    # Simple Jaccard-like correlation
                    correlation = min(count1, count2) / max(count1, count2)
                    
                    if correlation > 0.5:  # Only report notable correlations
                        correlations.append({
                            "feature_pair": sorted([feat1, feat2]),
                            "correlation": round(correlation, 2),
                            "significance": "high" if correlation > 0.7 else "medium"
                        })
    
    return {
        "correlations": correlations,
        "insights": [
            f"Found {len(correlations)} notable feature correlations"
        ] if correlations else ["No strong feature correlations detected"]
    }

async def _perform_expansion_analysis(
    self,
    analysis_data: Dict[str, Any],
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """Analyze expansion revenue opportunities"""
    
    opportunities = []
    segments = params.get("segments", [])
    
    # Extract real data if available
    total_mrr = 0
    user_counts = {}
    
    for dep_id, dep_result in analysis_data.items():
        if "data" in dep_result:
            for row in dep_result["data"]:
                if "mrr" in row:
                    total_mrr += row.get("mrr", 0)
                if "plan_type" in row:
                    plan = row["plan_type"]
                    user_counts[plan] = user_counts.get(plan, 0) + 1
    
    # Calculate real expansion opportunities
    if "usage_level" in segments and len(user_counts) > 0:
        # Estimate based on actual user counts
        for plan, count in user_counts.items():
            if count > 10:  # Only if reasonable sample size
                estimated_expansion = total_mrr * 0.1 * (count / sum(user_counts.values()))
                
                if estimated_expansion > 1000:  # Only report meaningful opportunities
                    opportunities.append({
                        "segment": f"{plan}_high_usage",
                        "expansion_potential": "high" if count > 50 else "medium",
                        "estimated_additional_mrr": round(estimated_expansion),
                        "confidence": 0.65  # Conservative
                    })
    
    return {
        "expansion_opportunities": opportunities,
        "total_opportunity_mrr": sum(opp.get("estimated_additional_mrr", 0) 
                                     for opp in opportunities)
    }
```

**Effort**: 2-3 hours  
**Testing**: Run `test_phase_4_3_workflows.py`

---

## Summary of All Fixes

| Fix # | Component | Lines | Issue | Effort | Priority |
|-------|-----------|-------|-------|--------|----------|
| 1 | server.py | 940, 1016 | Method references | 30 min | CRITICAL |
| 2 | query_optimizer.py | Multiple | Missing methods | 2-3 hrs | CRITICAL |
| 3 | conversation_memory.py | 144+ | Missing helpers | 3-4 hrs | CRITICAL |
| 4 | workflow_orchestrator.py | 751-844 | Mock implementations | 2-3 hrs | CRITICAL |

**Total Effort**: 8-12 hours for critical fixes  
**Estimated Timeline**: 1-2 days for experienced developer

