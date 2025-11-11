#!/usr/bin/env python3
"""
TDD Tests for ConversationMemory and StatisticalTester
Following Test-Driven Development methodology
"""

import asyncio

import pytest

from mcp_server.conversation_memory import ConversationMemory
from mcp_server.statistical_testing import StatisticalTester


class TestConversationMemoryModelUsed:
    """TDD tests for ConversationMemory with model_used parameter"""

    def test_add_interaction_with_model_used_parameter(self):
        """Test that add_interaction accepts model_used parameter"""
        memory = ConversationMemory()

        # Should accept model_used as a direct parameter
        interaction_id = memory.add_interaction(
            user_question="Test question",
            query_info={
                "dimensions": ["plan_type"],
                "measures": ["conversion_rate"],
            },
            result={"data": [{"plan_type": "basic", "conversion_rate": 0.8}]},
            insights=["Test insight"],
            model_used="users",  # NEW PARAMETER
        )

        assert interaction_id is not None
        assert len(memory.interactions) == 1

    def test_model_used_stored_in_interaction(self):
        """Test that model_used is properly stored in the interaction"""
        memory = ConversationMemory()

        memory.add_interaction(
            user_question="Test question",
            query_info={"dimensions": ["plan_type"], "measures": ["conversion_rate"]},
            result={"data": []},
            insights=[],
            model_used="users",
        )

        interaction = memory.interactions[0]
        assert interaction.model_used == "users"

    def test_model_used_backward_compatibility(self):
        """Test that model_used is optional (backward compatibility)"""
        memory = ConversationMemory()

        # Should work without model_used parameter (extracts from query_info)
        interaction_id = memory.add_interaction(
            user_question="Test question",
            query_info={
                "model": "events",
                "dimensions": ["feature"],
                "measures": ["count"],
            },
            result={"data": []},
            insights=[],
        )

        assert interaction_id is not None
        assert memory.interactions[0].model_used == "events"

    def test_model_used_overrides_query_info_model(self):
        """Test that explicit model_used parameter overrides query_info['model']"""
        memory = ConversationMemory()

        memory.add_interaction(
            user_question="Test question",
            query_info={
                "model": "old_model",
                "dimensions": [],
                "measures": [],
            },
            result={"data": []},
            insights=[],
            model_used="new_model",  # Should use this
        )

        assert memory.interactions[0].model_used == "new_model"

    def test_model_used_none_defaults_to_query_info(self):
        """Test that model_used=None falls back to query_info['model']"""
        memory = ConversationMemory()

        memory.add_interaction(
            user_question="Test question",
            query_info={"model": "events", "dimensions": [], "measures": []},
            result={"data": []},
            insights=[],
            model_used=None,  # Should fall back to query_info
        )

        assert memory.interactions[0].model_used == "events"

    def test_model_used_tracking_in_usage_stats(self):
        """Test that model_used is tracked in usage statistics"""
        memory = ConversationMemory()

        # Add multiple interactions with different models
        for model in ["users", "events", "users", "revenue"]:
            memory.add_interaction(
                user_question=f"Query {model}",
                query_info={"dimensions": [], "measures": []},
                result={"data": []},
                insights=[],
                model_used=model,
            )

        # Check usage tracking
        assert memory.model_usage["users"] == 2
        assert memory.model_usage["events"] == 1
        assert memory.model_usage["revenue"] == 1

    def test_model_used_in_conversation_context(self):
        """Test that model_used appears in conversation context"""
        memory = ConversationMemory()

        memory.add_interaction(
            user_question="Test question",
            query_info={"dimensions": [], "measures": []},
            result={"data": []},
            insights=[],
            model_used="users",
        )

        context = memory.get_conversation_context()
        assert "users" in context.get("models_explored", [])


class TestStatisticalTesterNullHandling:
    """TDD tests for StatisticalTester null and edge case handling"""

    def test_initialize_without_parameters(self):
        """Test that StatisticalTester can be initialized without parameters"""
        tester = StatisticalTester()
        assert tester is not None
        assert tester.min_sample_size == 30

    @pytest.mark.asyncio
    async def test_validate_result_with_none_data(self):
        """Test that validate_result handles None data gracefully"""
        tester = StatisticalTester()

        result = await tester.validate_result(
            result={"data": None}, dimensions=["plan_type"]
        )

        assert result is not None
        assert result["valid"] is False
        assert len(result["warnings"]) > 0

    @pytest.mark.asyncio
    async def test_validate_result_with_empty_data(self):
        """Test that validate_result handles empty data gracefully"""
        tester = StatisticalTester()

        result = await tester.validate_result(result={"data": []}, dimensions=[])

        assert result is not None
        assert result["valid"] is False

    @pytest.mark.asyncio
    async def test_validate_result_with_missing_result_key(self):
        """Test that validate_result handles missing 'data' key gracefully"""
        tester = StatisticalTester()

        result = await tester.validate_result(result={}, dimensions=[])

        assert result is not None
        assert result["valid"] is False

    @pytest.mark.asyncio
    async def test_auto_test_comparison_with_none_data(self):
        """Test that auto_test_comparison handles None data gracefully"""
        tester = StatisticalTester()

        result = await tester.auto_test_comparison(
            result={"data": None}, dimensions=["plan_type"], measures=["conversion"]
        )

        # Should return None or empty result, not crash
        assert result is None

    @pytest.mark.asyncio
    async def test_auto_test_comparison_with_empty_data(self):
        """Test that auto_test_comparison handles empty data gracefully"""
        tester = StatisticalTester()

        result = await tester.auto_test_comparison(
            result={"data": []}, dimensions=[], measures=[]
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_auto_test_comparison_with_invalid_columns(self):
        """Test that auto_test_comparison handles missing columns gracefully"""
        tester = StatisticalTester()

        result = await tester.auto_test_comparison(
            result={"data": [{"wrong_col": 1}]},
            dimensions=["plan_type"],
            measures=["conversion"],
        )

        assert result is None  # Should return None, not crash

    @pytest.mark.asyncio
    async def test_auto_test_comparison_with_insufficient_groups(self):
        """Test that auto_test_comparison handles single group gracefully"""
        tester = StatisticalTester()

        result = await tester.auto_test_comparison(
            result={
                "data": [
                    {"plan_type": "basic", "conversion": 0.8},
                    {"plan_type": "basic", "conversion": 0.7},
                ]
            },
            dimensions=["plan_type"],
            measures=["conversion"],
        )

        # Only one group, can't compare
        assert result is None

    @pytest.mark.asyncio
    async def test_validate_result_with_small_sample(self):
        """Test that validate_result warns about small sample sizes"""
        tester = StatisticalTester()

        result = await tester.validate_result(
            result={"data": [{"plan_type": "basic", "value": i} for i in range(10)]},
            dimensions=["plan_type"],
        )

        assert result is not None
        assert len(result["warnings"]) > 0
        assert any("Small sample size" in w for w in result["warnings"])

    @pytest.mark.asyncio
    async def test_run_significance_tests_with_none_data(self):
        """Test that run_significance_tests handles None data gracefully"""
        tester = StatisticalTester()

        result = await tester.run_significance_tests(
            data={"data": None},
            comparison_type="groups",
            dimensions=["plan_type"],
            measures=["conversion"],
        )

        # Should return None or error dict, not crash
        assert result is None or "error" in result or result is not None


class TestStatisticalTesterWithValidData:
    """TDD tests for StatisticalTester with valid data"""

    @pytest.mark.asyncio
    async def test_validate_result_with_valid_data(self):
        """Test that validate_result works correctly with valid data"""
        tester = StatisticalTester()

        result = await tester.validate_result(
            result={
                "data": [
                    {"plan_type": "basic", "conversion": 0.8}
                    for _ in range(50)
                ]
            },
            dimensions=["plan_type"],
        )

        assert result is not None
        assert result["valid"] is True
        assert "sample_sizes" in result
        assert result["sample_sizes"]["total"] == 50

    @pytest.mark.asyncio
    async def test_auto_test_comparison_with_valid_data(self):
        """Test that auto_test_comparison works correctly with valid data"""
        tester = StatisticalTester()

        # Create data with two distinct groups
        data = []
        for _ in range(30):
            data.append({"plan_type": "basic", "conversion": 0.8})
        for _ in range(30):
            data.append({"plan_type": "pro", "conversion": 0.6})

        result = await tester.auto_test_comparison(
            result={"data": data},
            dimensions=["plan_type"],
            measures=["conversion"],
        )

        assert result is not None
        assert "test_type" in result
        assert "p_value" in result
        assert "significant" in result


class TestIntegration:
    """Integration tests for ConversationMemory and StatisticalTester"""

    @pytest.mark.asyncio
    async def test_memory_and_stats_integration(self):
        """Test that ConversationMemory and StatisticalTester work together"""
        memory = ConversationMemory()
        tester = StatisticalTester()

        # Create test data
        data = [
            {"plan_type": "basic", "conversion": 0.8},
            {"plan_type": "pro", "conversion": 0.6},
        ] * 20

        # Run statistical test
        stats_result = await tester.auto_test_comparison(
            result={"data": data},
            dimensions=["plan_type"],
            measures=["conversion"],
        )

        # Add to conversation memory
        interaction_id = memory.add_interaction(
            user_question="Compare conversion by plan type",
            query_info={"dimensions": ["plan_type"], "measures": ["conversion"]},
            result={"data": data, "execution_time_ms": 25.5},
            insights=["Basic plan has higher conversion"],
            statistical_analysis=stats_result,
            model_used="users",
        )

        assert interaction_id is not None
        assert len(memory.interactions) == 1
        assert memory.interactions[0].statistical_tests is not None
        assert memory.interactions[0].model_used == "users"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
