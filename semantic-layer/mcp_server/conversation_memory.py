#!/usr/bin/env python3
"""
Conversation Memory Manager for AI Analyst

Tracks conversation context, analysis history, and user patterns to enable
sophisticated multi-turn analytical workflows and contextual insights.
"""

import hashlib
import json
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class AnalysisInteraction:
    """Represents a single analysis interaction"""

    timestamp: str
    user_question: str
    model_used: str
    dimensions: List[str]
    measures: List[str]
    filters: Dict[str, Any]
    result_summary: Dict[str, Any]
    insights_generated: List[str]
    statistical_tests: Optional[Dict[str, Any]]
    execution_time_ms: float
    interaction_id: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UserInterest:
    """Tracks user's analytical interests and patterns"""

    topic: str
    frequency: int
    last_accessed: str
    related_dimensions: Set[str]
    related_measures: Set[str]
    typical_filters: Dict[str, Any]


class ConversationMemory:
    """Manages conversation context and analytical memory"""

    def __init__(self, max_interactions: int = 50, context_window_hours: int = 24):
        self.max_interactions = max_interactions
        self.context_window_hours = context_window_hours

        # Core memory stores
        self.interactions: List[AnalysisInteraction] = []
        self.user_interests: Dict[str, UserInterest] = {}
        self.discovered_patterns: List[Dict[str, Any]] = []

        # Analysis tracking
        self.dimension_usage = Counter()
        self.measure_usage = Counter()
        self.model_usage = Counter()
        self.filter_patterns = defaultdict(Counter)

        # Performance tracking
        self.query_performance = {}
        self.common_sequences = []

    def add_interaction(
        self,
        user_question: str,
        query_info: Dict[str, Any],
        result: Dict[str, Any],
        insights: List[str],
        statistical_analysis: Optional[Dict[str, Any]] = None,
        model_used: Optional[str] = None,
    ) -> str:
        """Add a new analysis interaction to memory

        Args:
            user_question: The user's question or query
            query_info: Dictionary containing query details (model, dimensions, measures, filters)
            result: Query execution results
            insights: List of insights generated from the query
            statistical_analysis: Optional statistical test results
            model_used: Optional explicit model name (overrides query_info['model'])

        Returns:
            interaction_id: Unique identifier for this interaction
        """

        interaction_id = self._generate_interaction_id(user_question, query_info)

        # Use explicit model_used parameter if provided, otherwise fall back to query_info
        effective_model = model_used if model_used is not None else query_info.get("model", "")

        interaction = AnalysisInteraction(
            timestamp=datetime.now().isoformat(),
            user_question=user_question,
            model_used=effective_model,
            dimensions=query_info.get("dimensions", []),
            measures=query_info.get("measures", []),
            filters=query_info.get("filters", {}),
            result_summary=self._summarize_result(result),
            insights_generated=insights,
            statistical_tests=statistical_analysis,
            execution_time_ms=result.get("execution_time_ms", 0),
            interaction_id=interaction_id,
        )

        self.interactions.append(interaction)

        # Update usage patterns
        self._update_usage_patterns(interaction)

        # Update user interests
        self._update_user_interests(interaction)

        # Cleanup old interactions
        self._cleanup_old_interactions()

        return interaction_id

    def get_conversation_context(
        self, hours_back: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get conversation context for the specified time window"""

        if hours_back is None:
            hours_back = self.context_window_hours

        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        recent_interactions = [
            interaction
            for interaction in self.interactions
            if datetime.fromisoformat(interaction.timestamp) > cutoff_time
        ]

        if not recent_interactions:
            return {"status": "no_recent_context"}

        # Analyze recent conversation themes
        themes = self._extract_conversation_themes(recent_interactions)

        # Identify current analytical focus
        current_focus = self._identify_current_focus(recent_interactions)

        # Track evolution of questions
        question_evolution = self._analyze_question_evolution(recent_interactions)

        return {
            "recent_interactions_count": len(recent_interactions),
            "time_window_hours": hours_back,
            "conversation_themes": themes,
            "current_analytical_focus": current_focus,
            "question_evolution": question_evolution,
            "models_explored": list(set(i.model_used for i in recent_interactions)),
            "dimensions_explored": list(
                set(d for i in recent_interactions for d in i.dimensions)
            ),
            "measures_explored": list(
                set(m for i in recent_interactions for m in i.measures)
            ),
        }

    def suggest_contextual_next_steps(
        self, current_result: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """Generate contextually relevant next analysis suggestions"""

        suggestions = []
        context = self.get_conversation_context()

        if context.get("status") == "no_recent_context":
            return self._get_starter_suggestions()

        current_focus = context.get("current_analytical_focus", {})
        recent_themes = context.get("conversation_themes", [])

        # Suggest deepening current analysis
        if current_focus:
            suggestions.extend(self._suggest_deepening_analysis(current_focus))

        # Suggest expanding scope based on themes
        if recent_themes:
            suggestions.extend(self._suggest_expanding_scope(recent_themes))

        # Suggest following up on discovered patterns
        for pattern in self.discovered_patterns[-3:]:  # Last 3 patterns
            suggestions.extend(self._suggest_pattern_followup(pattern))

        # Suggest statistical validation for recent findings
        suggestions.extend(self._suggest_statistical_validation())

        # Suggest time-based analysis if not recently done
        suggestions.extend(self._suggest_temporal_analysis())

        # Remove duplicates and prioritize
        unique_suggestions = self._deduplicate_suggestions(suggestions)

        return unique_suggestions[:6]  # Return top 6 suggestions

    def identify_analysis_patterns(self) -> List[Dict[str, Any]]:
        """Identify patterns in user's analytical behavior"""

        patterns = []

        # Common dimension combinations
        dimension_combos = Counter()
        for interaction in self.interactions:
            if len(interaction.dimensions) > 1:
                combo = tuple(sorted(interaction.dimensions))
                dimension_combos[combo] += 1

        for combo, frequency in dimension_combos.most_common(5):
            if frequency > 1:
                patterns.append(
                    {
                        "type": "dimension_combination",
                        "pattern": list(combo),
                        "frequency": frequency,
                        "description": f"Frequently analyzes {' + '.join(combo)}",
                    }
                )

        # Measure progression patterns
        measure_sequences = self._find_measure_sequences()
        for sequence in measure_sequences:
            patterns.append(
                {
                    "type": "measure_progression",
                    "pattern": sequence,
                    "description": f"Typical analysis flow: {' → '.join(sequence)}",
                }
            )

        # Model preferences
        model_prefs = self.model_usage.most_common(3)
        for model, frequency in model_prefs:
            if frequency > 2:
                patterns.append(
                    {
                        "type": "model_preference",
                        "pattern": model,
                        "frequency": frequency,
                        "description": f"Frequently analyzes {model} data",
                    }
                )

        self.discovered_patterns.extend(patterns)
        return patterns

    def get_query_recommendations(
        self, current_query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get recommendations for optimizing current query based on history"""

        model = current_query.get("model")
        dimensions = current_query.get("dimensions", [])
        measures = current_query.get("measures", [])

        recommendations = {
            "additional_dimensions": [],
            "additional_measures": [],
            "alternative_approaches": [],
            "performance_notes": [],
        }

        # Suggest additional dimensions based on common combinations
        for interaction in self.interactions:
            if interaction.model_used == model and any(
                d in interaction.dimensions for d in dimensions
            ):

                for dim in interaction.dimensions:
                    if (
                        dim not in dimensions
                        and dim not in recommendations["additional_dimensions"]
                    ):
                        recommendations["additional_dimensions"].append(dim)

        # Suggest additional measures commonly used with current measures
        for interaction in self.interactions:
            if any(m in interaction.measures for m in measures):
                for measure in interaction.measures:
                    if (
                        measure not in measures
                        and measure not in recommendations["additional_measures"]
                    ):
                        recommendations["additional_measures"].append(measure)

        # Performance recommendations
        similar_queries = self._find_similar_queries(current_query)
        if similar_queries:
            avg_time = sum(q.execution_time_ms for q in similar_queries) / len(
                similar_queries
            )
            recommendations["performance_notes"].append(
                f"Similar queries typically execute in {avg_time:.1f}ms"
            )

        return recommendations

    def export_conversation_summary(self) -> Dict[str, Any]:
        """Export a comprehensive summary of the conversation"""

        if not self.interactions:
            return {"status": "no_interactions"}

        summary = {
            "conversation_metadata": {
                "total_interactions": len(self.interactions),
                "date_range": {
                    "start": self.interactions[0].timestamp,
                    "end": self.interactions[-1].timestamp,
                },
                "total_analysis_time_ms": sum(
                    i.execution_time_ms for i in self.interactions
                ),
            },
            "analytical_coverage": {
                "models_explored": dict(self.model_usage),
                "dimensions_explored": dict(self.dimension_usage),
                "measures_explored": dict(self.measure_usage),
                "unique_filters": len(set(str(i.filters) for i in self.interactions)),
            },
            "insights_generated": {
                "total_insights": sum(
                    len(i.insights_generated) for i in self.interactions
                ),
                "statistical_tests_run": sum(
                    1 for i in self.interactions if i.statistical_tests
                ),
                "key_findings": self._extract_key_findings(),
            },
            "user_interests": {
                name: asdict(interest) for name, interest in self.user_interests.items()
            },
            "discovered_patterns": self.discovered_patterns,
            "conversation_themes": self._extract_conversation_themes(self.interactions),
        }

        return summary

    # Private helper methods

    def _generate_interaction_id(
        self, question: str, query_info: Dict[str, Any]
    ) -> str:
        """Generate unique ID for interaction"""
        content = f"{question}_{query_info.get('model', '')}_{time.time()}"
        return hashlib.sha256(content.encode()).hexdigest()[:8]

    def _summarize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of query results"""
        return {
            "row_count": result.get("row_count", 0),
            "column_count": result.get("column_count", 0),
            "execution_time_ms": result.get("execution_time_ms", 0),
            "has_data": len(result.get("data", [])) > 0,
            "data_sample": result.get("data", [])[:3] if result.get("data") else [],
        }

    def _update_usage_patterns(self, interaction: AnalysisInteraction):
        """Update usage pattern counters"""
        self.model_usage[interaction.model_used] += 1

        for dim in interaction.dimensions:
            self.dimension_usage[dim] += 1

        for measure in interaction.measures:
            self.measure_usage[measure] += 1

        for key, value in interaction.filters.items():
            self.filter_patterns[key][str(value)] += 1

    def _update_user_interests(self, interaction: AnalysisInteraction):
        """Update user interest tracking"""
        # Extract topic from model and measures
        topic = f"{interaction.model_used}_analysis"

        if topic in self.user_interests:
            interest = self.user_interests[topic]
            interest.frequency += 1
            interest.last_accessed = interaction.timestamp
            interest.related_dimensions.update(interaction.dimensions)
            interest.related_measures.update(interaction.measures)
        else:
            self.user_interests[topic] = UserInterest(
                topic=topic,
                frequency=1,
                last_accessed=interaction.timestamp,
                related_dimensions=set(interaction.dimensions),
                related_measures=set(interaction.measures),
                typical_filters=interaction.filters.copy(),
            )

    def _cleanup_old_interactions(self):
        """Remove old interactions to manage memory"""
        if len(self.interactions) > self.max_interactions:
            self.interactions = self.interactions[-self.max_interactions :]

    def _extract_conversation_themes(
        self, interactions: List[AnalysisInteraction]
    ) -> List[str]:
        """Extract thematic patterns from conversation"""
        themes = []

        # Model-based themes
        model_focus = Counter(i.model_used for i in interactions)
        for model, count in model_focus.most_common(3):
            if count > 1:
                themes.append(f"{model}_focused_analysis")

        # Dimension-based themes
        dim_focus = Counter(d for i in interactions for d in i.dimensions)
        for dim, count in dim_focus.most_common(2):
            if count > 1:
                themes.append(f"{dim}_segmentation")

        return themes

    def _identify_current_focus(
        self, interactions: List[AnalysisInteraction]
    ) -> Dict[str, Any]:
        """Identify current analytical focus"""
        if not interactions:
            return {}

        latest = interactions[-3:]  # Last 3 interactions

        return {
            "primary_model": Counter(i.model_used for i in latest).most_common(1)[0][0],
            "key_dimensions": [d for i in latest for d in i.dimensions],
            "key_measures": [m for i in latest for m in i.measures],
            "analysis_depth": len(latest),
        }

    def _analyze_question_evolution(
        self, interactions: List[AnalysisInteraction]
    ) -> List[str]:
        """Analyze how questions have evolved"""
        if len(interactions) < 2:
            return []

        evolution = []
        for i in range(1, len(interactions)):
            prev = interactions[i - 1]
            curr = interactions[i]

            if curr.model_used != prev.model_used:
                evolution.append(
                    f"switched_from_{prev.model_used}_to_{curr.model_used}"
                )
            elif len(curr.dimensions) > len(prev.dimensions):
                evolution.append("added_dimensions")
            elif len(curr.measures) > len(prev.measures):
                evolution.append("expanded_metrics")
            elif curr.filters != prev.filters:
                evolution.append("refined_filters")

        return evolution

    def _suggest_deepening_analysis(
        self, current_focus: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Suggest ways to deepen current analysis"""
        suggestions = []

        model = current_focus.get("primary_model", "")
        dimensions = current_focus.get("key_dimensions", [])
        measures = current_focus.get("key_measures", [])

        if model and dimensions:
            suggestions.append(
                {
                    "question": f"What statistical tests can validate the {model} patterns we're seeing?",
                    "reason": "Add statistical rigor to current findings",
                    "type": "statistical_validation",
                }
            )

        if len(dimensions) == 1:
            suggestions.append(
                {
                    "question": f"How do the {model} results vary when we add additional segmentation?",
                    "reason": "Expand dimensional analysis",
                    "type": "dimensional_expansion",
                }
            )

        return suggestions

    def _suggest_expanding_scope(self, themes: List[str]) -> List[Dict[str, str]]:
        """Suggest expanding analysis scope"""
        suggestions = []

        for theme in themes[:2]:  # Focus on top 2 themes
            if "analysis" in theme:
                model = theme.replace("_focused_analysis", "")
                suggestions.append(
                    {
                        "question": f"How does {model} performance compare across different time periods?",
                        "reason": "Add temporal dimension to analysis",
                        "type": "temporal_expansion",
                    }
                )

        return suggestions

    def _suggest_pattern_followup(
        self, pattern: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Suggest following up on discovered patterns"""
        suggestions = []

        if pattern["type"] == "dimension_combination":
            combo = pattern["pattern"]
            suggestions.append(
                {
                    "question": f"What drives the differences we see in {' and '.join(combo)} analysis?",
                    "reason": "Investigate causal factors",
                    "type": "causal_investigation",
                }
            )

        return suggestions

    def _suggest_statistical_validation(self) -> List[Dict[str, str]]:
        """Suggest statistical validation for recent findings"""
        suggestions = []

        recent_comparisons = [
            i
            for i in self.interactions[-5:]
            if len(i.dimensions) > 0 and len(i.measures) > 0
        ]

        if recent_comparisons and not any(
            i.statistical_tests for i in recent_comparisons
        ):
            suggestions.append(
                {
                    "question": "Are the differences we've observed statistically significant?",
                    "reason": "Validate findings with statistical testing",
                    "type": "statistical_validation",
                }
            )

        return suggestions

    def _suggest_temporal_analysis(self) -> List[Dict[str, str]]:
        """Suggest time-based analysis if not recently done"""
        suggestions = []

        has_recent_temporal = any(
            "time" in str(i.dimensions).lower() or "date" in str(i.dimensions).lower()
            for i in self.interactions[-5:]
        )

        if not has_recent_temporal:
            suggestions.append(
                {
                    "question": "How have these metrics changed over time?",
                    "reason": "Add temporal perspective to analysis",
                    "type": "temporal_analysis",
                }
            )

        return suggestions

    def _get_starter_suggestions(self) -> List[Dict[str, str]]:
        """Get starter suggestions for new conversations"""
        return [
            {
                "question": "What are our key performance metrics?",
                "reason": "Establish baseline understanding",
                "type": "baseline_exploration",
            },
            {
                "question": "How do our metrics vary by customer segment?",
                "reason": "Understand segment performance",
                "type": "segmentation_analysis",
            },
            {
                "question": "What trends are we seeing in our key metrics?",
                "reason": "Identify temporal patterns",
                "type": "trend_analysis",
            },
        ]

    def _deduplicate_suggestions(
        self, suggestions: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Remove duplicate suggestions and prioritize"""
        seen_questions = set()
        unique_suggestions = []

        # Prioritize by type
        type_priority = {
            "statistical_validation": 1,
            "causal_investigation": 2,
            "dimensional_expansion": 3,
            "temporal_analysis": 4,
            "baseline_exploration": 5,
        }

        sorted_suggestions = sorted(
            suggestions, key=lambda x: type_priority.get(x.get("type", ""), 99)
        )

        for suggestion in sorted_suggestions:
            question_key = suggestion["question"].lower().strip()
            if question_key not in seen_questions:
                seen_questions.add(question_key)
                unique_suggestions.append(suggestion)

        return unique_suggestions

    def _find_measure_sequences(self) -> List[List[str]]:
        """Find common sequences of measures in analysis"""
        sequences = []

        if len(self.interactions) < 3:
            return sequences

        for i in range(len(self.interactions) - 2):
            sequence = [
                (
                    self.interactions[i].measures[0]
                    if self.interactions[i].measures
                    else ""
                ),
                (
                    self.interactions[i + 1].measures[0]
                    if self.interactions[i + 1].measures
                    else ""
                ),
                (
                    self.interactions[i + 2].measures[0]
                    if self.interactions[i + 2].measures
                    else ""
                ),
            ]

            if all(sequence) and sequence not in sequences:
                sequences.append(sequence)

        return sequences

    def _find_similar_queries(self, query: Dict[str, Any]) -> List[AnalysisInteraction]:
        """Find historically similar queries"""
        similar = []

        target_model = query.get("model", "")
        target_dims = set(query.get("dimensions", []))
        target_measures = set(query.get("measures", []))

        for interaction in self.interactions:
            if interaction.model_used == target_model:
                dim_overlap = len(target_dims & set(interaction.dimensions))
                measure_overlap = len(target_measures & set(interaction.measures))

                if dim_overlap > 0 or measure_overlap > 0:
                    similar.append(interaction)

        return similar

    def _extract_key_findings(self) -> List[str]:
        """Extract key findings from all interactions"""
        key_findings = []

        for interaction in self.interactions:
            # Look for insights with statistical significance
            for insight in interaction.insights_generated:
                if any(
                    keyword in insight.lower()
                    for keyword in [
                        "significant",
                        "higher",
                        "lower",
                        "trend",
                        "correlation",
                    ]
                ):
                    key_findings.append(insight)

        # Remove duplicates and limit
        return list(set(key_findings))[:10]

    def get_query_usage_patterns(self) -> Dict[str, Any]:
        """Get patterns in query usage over time"""
        if not self.interactions:
            return {"status": "no_data"}

        patterns = {
            "query_frequency_by_hour": defaultdict(int),
            "common_query_structures": [],
            "session_patterns": [],
            "complexity_trends": [],
        }

        # Analyze query frequency by hour
        for interaction in self.interactions:
            try:
                hour = datetime.fromisoformat(interaction.timestamp).hour
                patterns["query_frequency_by_hour"][hour] += 1
            except:
                continue

        # Analyze common query structures
        structure_counts = Counter()
        for interaction in self.interactions:
            structure = f"{len(interaction.dimensions)}D_{len(interaction.measures)}M"
            structure_counts[structure] += 1

        patterns["common_query_structures"] = [
            {
                "structure": structure,
                "count": count,
                "description": f"{structure.split('_')[0]} dimensions, {structure.split('_')[1]} measures",
            }
            for structure, count in structure_counts.most_common(5)
        ]

        # Analyze complexity trends over time
        recent_interactions = (
            self.interactions[-20:]
            if len(self.interactions) > 20
            else self.interactions
        )
        for i, interaction in enumerate(recent_interactions):
            complexity_score = (
                len(interaction.dimensions) * 2
                + len(interaction.measures)
                + len(interaction.filters)
            )
            patterns["complexity_trends"].append(
                {
                    "interaction_index": i,
                    "complexity_score": complexity_score,
                    "timestamp": interaction.timestamp,
                }
            )

        return patterns

    def get_model_usage_stats(self) -> Dict[str, Any]:
        """Get statistics about model usage patterns"""
        if not self.interactions:
            return {"status": "no_data"}

        stats = {
            "model_frequency": dict(self.model_usage.most_common()),
            "model_performance": {},
            "model_preferences_over_time": [],
            "model_combinations": [],
        }

        # Calculate performance stats by model
        for model in self.model_usage.keys():
            model_interactions = [i for i in self.interactions if i.model_used == model]
            if model_interactions:
                execution_times = [i.execution_time_ms for i in model_interactions]
                insights_count = sum(
                    len(i.insights_generated) for i in model_interactions
                )

                stats["model_performance"][model] = {
                    "avg_execution_time_ms": sum(execution_times)
                    / len(execution_times),
                    "total_queries": len(model_interactions),
                    "total_insights_generated": insights_count,
                    "avg_insights_per_query": (
                        insights_count / len(model_interactions)
                        if model_interactions
                        else 0
                    ),
                }

        # Track model preference changes over time
        if len(self.interactions) >= 5:
            for i in range(0, len(self.interactions) - 4, 5):  # Every 5 interactions
                window = self.interactions[i : i + 5]
                model_counts = Counter(interaction.model_used for interaction in window)
                most_common = model_counts.most_common(1)
                if most_common:
                    stats["model_preferences_over_time"].append(
                        {
                            "window_start": i,
                            "preferred_model": most_common[0][0],
                            "usage_count": most_common[0][1],
                        }
                    )

        # Find model combinations (switching patterns)
        if len(self.interactions) > 1:
            for i in range(len(self.interactions) - 1):
                current_model = self.interactions[i].model_used
                next_model = self.interactions[i + 1].model_used
                if current_model != next_model:
                    stats["model_combinations"].append(
                        {
                            "from_model": current_model,
                            "to_model": next_model,
                            "transition_time": self.interactions[i + 1].timestamp,
                        }
                    )

        return stats

    def get_popular_dimension_combinations(self) -> Dict[str, Any]:
        """Get popular dimension combinations and their usage patterns"""
        if not self.interactions:
            return {"status": "no_data"}

        combinations = {
            "single_dimensions": Counter(),
            "dimension_pairs": Counter(),
            "dimension_triplets": Counter(),
            "popular_combinations": [],
            "dimension_correlation": {},
        }

        # Count single dimensions
        for interaction in self.interactions:
            for dim in interaction.dimensions:
                combinations["single_dimensions"][dim] += 1

        # Count dimension pairs
        for interaction in self.interactions:
            dims = sorted(interaction.dimensions)
            if len(dims) >= 2:
                for i in range(len(dims)):
                    for j in range(i + 1, len(dims)):
                        pair = (dims[i], dims[j])
                        combinations["dimension_pairs"][pair] += 1

        # Count dimension triplets
        for interaction in self.interactions:
            dims = sorted(interaction.dimensions)
            if len(dims) >= 3:
                for i in range(len(dims)):
                    for j in range(i + 1, len(dims)):
                        for k in range(j + 1, len(dims)):
                            triplet = (dims[i], dims[j], dims[k])
                            combinations["dimension_triplets"][triplet] += 1

        # Format popular combinations
        for pair, count in combinations["dimension_pairs"].most_common(5):
            combinations["popular_combinations"].append(
                {
                    "combination": list(pair),
                    "frequency": count,
                    "type": "pair",
                    "description": f"Often analyzed together: {' + '.join(pair)}",
                }
            )

        for triplet, count in combinations["dimension_triplets"].most_common(3):
            combinations["popular_combinations"].append(
                {
                    "combination": list(triplet),
                    "frequency": count,
                    "type": "triplet",
                    "description": f"Common three-way analysis: {' + '.join(triplet)}",
                }
            )

        # Calculate dimension correlation (which dimensions are often used together)
        for dim1 in combinations["single_dimensions"].keys():
            correlations = {}
            dim1_appearances = sum(1 for i in self.interactions if dim1 in i.dimensions)

            for dim2 in combinations["single_dimensions"].keys():
                if dim1 != dim2:
                    co_appearances = sum(
                        1
                        for i in self.interactions
                        if dim1 in i.dimensions and dim2 in i.dimensions
                    )
                    if dim1_appearances > 0:
                        correlation_score = co_appearances / dim1_appearances
                        if (
                            correlation_score > 0.3
                        ):  # Only include meaningful correlations
                            correlations[dim2] = correlation_score

            if correlations:
                combinations["dimension_correlation"][dim1] = correlations

        return combinations
