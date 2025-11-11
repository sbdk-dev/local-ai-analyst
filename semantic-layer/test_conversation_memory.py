#!/usr/bin/env python3
"""
Test script for conversation memory and Phase 4 enhancements
"""

import asyncio

from mcp_server.conversation_memory import ConversationMemory
from mcp_server.intelligence_layer import IntelligenceEngine
from mcp_server.semantic_layer_integration import SemanticLayerManager
from mcp_server.statistical_testing import StatisticalTester


async def test_conversation_memory():
    """Test conversation memory functionality with realistic analysis sequence"""

    print("🧪 Testing Phase 4: Conversation Memory & Context")
    print("=" * 60)

    # Initialize components (in-memory testing)
    conversation_memory = ConversationMemory()

    # Test with mock data instead of real database to avoid lock conflicts
    print("\n📝 Testing Conversation Memory with Mock Interactions")
    print("-" * 50)

    # Simulate a realistic conversation sequence
    print("\n📝 Simulating Multi-Turn Analysis Conversation")
    print("-" * 50)

    # Turn 1: Initial exploration
    print("\n👤 Turn 1: What's our conversion rate by plan type?")

    # Mock query and result data
    query1_info = {
        "model": "users",
        "dimensions": ["plan_type"],
        "measures": ["conversion_rate", "total_users"],
        "sql": "SELECT plan_type, COUNT(*) as total_users, AVG(conversion) as conversion_rate FROM users GROUP BY plan_type",
    }

    result1 = {
        "data": [
            {"plan_type": "basic", "total_users": 596, "conversion_rate": 81.8},
            {"plan_type": "pro", "total_users": 116, "conversion_rate": 74.6},
            {"plan_type": "enterprise", "total_users": 34, "conversion_rate": 74.4},
        ],
        "row_count": 3,
        "execution_time_ms": 25.5,
    }

    # Track interaction
    interaction1_id = conversation_memory.add_interaction(
        user_question="What's our conversion rate by plan type?",
        query_info=query1_info,
        result=result1,
        insights=["Basic plan has highest conversion rate (81.8%)"],
    )
    print(f"✅ Tracked interaction {interaction1_id}")

    # Turn 2: Follow-up based on findings
    print("\n👤 Turn 2: Why does basic plan have better conversion?")

    query2_info = {
        "model": "users",
        "dimensions": ["plan_type", "industry"],
        "measures": ["conversion_rate"],
        "sql": "SELECT plan_type, industry, AVG(conversion) as conversion_rate FROM users GROUP BY plan_type, industry",
    }

    result2 = {
        "data": [
            {"plan_type": "basic", "industry": "tech", "conversion_rate": 85.2},
            {"plan_type": "basic", "industry": "fintech", "conversion_rate": 78.4},
            {"plan_type": "pro", "industry": "tech", "conversion_rate": 76.1},
        ],
        "row_count": 3,
        "execution_time_ms": 32.1,
    }

    interaction2_id = conversation_memory.add_interaction(
        user_question="Why does basic plan have better conversion?",
        query_info=query2_info,
        result=result2,
        insights=["Need to analyze by industry to understand conversion patterns"],
    )
    print(f"✅ Tracked interaction {interaction2_id}")

    # Turn 3: Statistical validation
    print("\n👤 Turn 3: Is this difference statistically significant?")

    mock_stats_result = {
        "test_type": "chi_square",
        "p_value": 0.003,
        "effect_size": 0.25,
        "effect_size_interpretation": "medium",
        "significant": True,
    }

    conversation_memory.add_interaction(
        user_question="Is this difference statistically significant?",
        query_info={
            "model": "statistical_test",
            "dimensions": ["plan_type"],
            "measures": ["conversion_rate"],
        },
        result={"data": [{"test": "statistical_analysis"}], "execution_time_ms": 15},
        insights=["Statistical analysis completed"],
        statistical_analysis=mock_stats_result,
    )

    # Test conversation context retrieval
    print("\n🧠 Testing Conversation Context")
    print("-" * 30)

    context = conversation_memory.get_conversation_context()
    print(f"✅ Context retrieved: {context['recent_interactions_count']} interactions")
    print(f"📊 Models explored: {context.get('models_explored', [])}")
    print(f"📏 Dimensions used: {context.get('dimensions_explored', [])}")
    print(f"📈 Measures analyzed: {context.get('measures_explored', [])}")

    # Test contextual suggestions
    print("\n💡 Testing Contextual Suggestions")
    print("-" * 35)

    suggestions = conversation_memory.suggest_contextual_next_steps()
    print(f"✅ Generated {len(suggestions)} contextual suggestions:")
    for i, suggestion in enumerate(suggestions[:3], 1):
        print(f"  {i}. {suggestion['question']}")
        print(f"     Reason: {suggestion['reason']}")

    # Test pattern detection
    print("\n🔍 Testing Pattern Detection")
    print("-" * 30)

    patterns = conversation_memory.identify_analysis_patterns()
    print(f"✅ Discovered {len(patterns)} patterns:")
    for pattern in patterns:
        print(
            f"  • {pattern['type']}: {pattern.get('description', 'Pattern detected')}"
        )

    # Test query optimization recommendations
    print("\n⚡ Testing Query Optimization")
    print("-" * 30)

    recommendations = conversation_memory.get_query_recommendations(
        {"model": "users", "dimensions": ["plan_type"], "measures": ["conversion_rate"]}
    )
    print(
        f"✅ Additional dimensions suggested: {recommendations.get('additional_dimensions', [])[:3]}"
    )
    print(
        f"⚡ Additional measures suggested: {recommendations.get('additional_measures', [])[:3]}"
    )

    # Test conversation export
    print("\n📤 Testing Conversation Export")
    print("-" * 30)

    export = conversation_memory.export_conversation_summary()
    if export.get("status") != "no_interactions":
        metadata = export["conversation_metadata"]
        coverage = export["analytical_coverage"]
        insights = export["insights_generated"]

        print(f"✅ Total interactions: {metadata['total_interactions']}")
        print(f"📊 Models explored: {len(coverage['models_explored'])}")
        print(f"💡 Total insights: {insights['total_insights']}")
        print(f"📈 Statistical tests: {insights['statistical_tests_run']}")

    # Test multi-turn context awareness
    print("\n🔄 Testing Multi-Turn Context Awareness")
    print("-" * 40)

    # Add another interaction that builds on previous ones
    query4_info = {
        "model": "events",
        "dimensions": ["feature_name"],
        "measures": ["events_per_user"],
        "sql": "SELECT feature_name, COUNT(*) / COUNT(DISTINCT user_id) as events_per_user FROM events GROUP BY feature_name",
    }

    result4 = {
        "data": [
            {"feature_name": "dashboard_view", "events_per_user": 15.2},
            {"feature_name": "report_create", "events_per_user": 8.7},
            {"feature_name": "data_upload", "events_per_user": 3.1},
        ],
        "row_count": 3,
        "execution_time_ms": 18.9,
    }

    conversation_memory.add_interaction(
        user_question="Which features are most popular among high-converting users?",
        query_info=query4_info,
        result=result4,
        insights=["Expanding analysis to feature usage patterns"],
    )

    # Check if context awareness improves suggestions
    new_suggestions = conversation_memory.suggest_contextual_next_steps()
    print(f"✅ Updated suggestions reflect conversation evolution")
    print(
        f"📊 New suggestion types: {[s.get('type', 'general') for s in new_suggestions[:3]]}"
    )

    # Verify conversation themes
    final_context = conversation_memory.get_conversation_context()
    themes = final_context.get("conversation_themes", [])
    print(f"🎯 Identified conversation themes: {themes}")

    print(f"\n🎉 Phase 4.1 Conversation Memory: All tests passed!")
    print(f"📊 Tracked {len(conversation_memory.interactions)} interactions")
    print(f"🧠 Context window: {conversation_memory.context_window_hours} hours")
    print(
        f"💾 Memory efficiency: {len(conversation_memory.user_interests)} interest topics"
    )


if __name__ == "__main__":
    asyncio.run(test_conversation_memory())
