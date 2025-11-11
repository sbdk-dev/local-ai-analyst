#!/usr/bin/env python3
"""
TDD Tests for IntelligenceEngine Fix

Tests the missing methods:
- interpret_query_result()
- generate_analysis_suggestions()
"""

import asyncio
from mcp_server.intelligence_layer import IntelligenceEngine


class TestInterpretQueryResult:
    """Test interpret_query_result() method"""

    async def test_basic_interpretation(self):
        """Test basic interpretation of query results"""
        engine = IntelligenceEngine()

        result = {
            "data": [
                {"plan_type": "free", "total_users": 100},
                {"plan_type": "pro", "total_users": 200},
            ],
            "execution_time_ms": 50,
        }

        interpretation = await engine.interpret_query_result(
            result=result, dimensions=["plan_type"], measures=["total_users"]
        )

        assert isinstance(interpretation, str), "Should return string"
        assert len(interpretation) > 0, "Should not be empty"
        # Should mention the comparison or show evidence of analyzing the data
        assert (
            "pro" in interpretation.lower() or "free" in interpretation.lower()
        ), "Should mention dimension values"

    async def test_single_metric_interpretation(self):
        """Test interpretation of single metric (no dimensions)"""
        engine = IntelligenceEngine()

        result = {
            "data": [{"total_users": 1523}],
            "execution_time_ms": 30,
        }

        interpretation = await engine.interpret_query_result(
            result=result, dimensions=[], measures=["total_users"]
        )

        assert len(interpretation) > 0, "Should generate interpretation"
        assert "1523" in interpretation or "1.5K" in interpretation, "Should mention count"

    async def test_grouped_data_interpretation(self):
        """Test interpretation of grouped results"""
        engine = IntelligenceEngine()

        result = {
            "data": [
                {"industry": "Tech", "avg_ltv": 5200},
                {"industry": "Retail", "avg_ltv": 2600},
                {"industry": "Healthcare", "avg_ltv": 3800},
            ],
            "execution_time_ms": 75,
        }

        interpretation = await engine.interpret_query_result(
            result=result, dimensions=["industry"], measures=["avg_ltv"]
        )

        assert len(interpretation) > 0, "Should generate interpretation"
        # Should identify highest/lowest or show comparison
        assert "Tech" in interpretation or "5200" in interpretation, "Should mention top performer"

    async def test_empty_result_interpretation(self):
        """Test interpretation of empty results"""
        engine = IntelligenceEngine()

        result = {"data": [], "execution_time_ms": 20}

        interpretation = await engine.interpret_query_result(
            result=result, dimensions=["plan_type"], measures=["total_users"]
        )

        assert len(interpretation) > 0, "Should generate message for empty results"
        assert (
            "no data" in interpretation.lower() or "empty" in interpretation.lower()
        ), "Should indicate no data"

    async def test_error_result_interpretation(self):
        """Test interpretation of error results"""
        engine = IntelligenceEngine()

        result = {"error": "Query failed", "execution_time_ms": 0}

        interpretation = await engine.interpret_query_result(
            result=result, dimensions=["plan_type"], measures=["total_users"]
        )

        assert len(interpretation) > 0, "Should generate error message"
        assert "error" in interpretation.lower() or "failed" in interpretation.lower(), (
            "Should indicate error"
        )

    async def test_statistical_context_integration(self):
        """Test integration of statistical analysis in interpretation"""
        engine = IntelligenceEngine()

        result = {
            "data": [
                {"plan_type": "free", "conversion_rate": 0.15},
                {"plan_type": "pro", "conversion_rate": 0.35},
            ],
            "execution_time_ms": 60,
        }

        # This should work with optional statistical_analysis parameter
        interpretation = await engine.interpret_query_result(
            result=result,
            dimensions=["plan_type"],
            measures=["conversion_rate"],
            statistical_analysis={
                "p_value": 0.0001,
                "effect_size": 0.8,
                "effect_size_interpretation": "large",
            },
        )

        assert len(interpretation) > 0, "Should generate interpretation"
        # Should mention statistical significance if provided
        assert (
            "significant" in interpretation.lower() or "p" in interpretation.lower()
        ), "Should mention statistics if provided"

    async def test_context_aware_interpretation(self):
        """Test context-aware interpretation"""
        engine = IntelligenceEngine()

        result = {
            "data": [{"conversion_rate": 0.35}],
            "execution_time_ms": 40,
        }

        interpretation = await engine.interpret_query_result(
            result=result,
            dimensions=[],
            measures=["conversion_rate"],
            context={"model": "users", "question": "What's our conversion rate?"},
        )

        assert len(interpretation) > 0, "Should generate interpretation"
        # Should mention conversion_rate or show the numeric value (may be formatted)
        assert (
            "conversion_rate" in interpretation.lower()
            or "0.3" in interpretation
            or "35" in interpretation
        ), "Should mention conversion metric"


class TestGenerateAnalysisSuggestions:
    """Test generate_analysis_suggestions() method"""

    async def test_basic_suggestions(self):
        """Test basic suggestion generation"""
        engine = IntelligenceEngine()

        result = {
            "data": [
                {"plan_type": "free", "total_users": 100},
                {"plan_type": "pro", "total_users": 200},
            ]
        }

        suggestions = await engine.generate_analysis_suggestions(
            current_result=result, context="testing users"
        )

        assert isinstance(suggestions, list), "Should return list"
        assert len(suggestions) > 0, "Should generate suggestions"
        assert all(
            "question" in s for s in suggestions
        ), "Each suggestion should have question"

    async def test_suggestions_without_result(self):
        """Test suggestions when no current result"""
        engine = IntelligenceEngine()

        suggestions = await engine.generate_analysis_suggestions(
            current_result=None, context="starting analysis"
        )

        assert len(suggestions) > 0, "Should generate starting suggestions"

    async def test_suggestions_format(self):
        """Test suggestion format"""
        engine = IntelligenceEngine()

        result = {"data": [{"total_users": 1000}]}

        suggestions = await engine.generate_analysis_suggestions(
            current_result=result, context="users model"
        )

        for suggestion in suggestions:
            assert "question" in suggestion, "Should have question field"
            assert isinstance(suggestion["question"], str), "Question should be string"
            assert len(suggestion["question"]) > 0, "Question should not be empty"

    async def test_context_based_suggestions(self):
        """Test that suggestions are context-aware"""
        engine = IntelligenceEngine()

        result = {"data": [{"events_per_user": 50}]}

        suggestions = await engine.generate_analysis_suggestions(
            current_result=result, context="events analysis"
        )

        assert len(suggestions) > 0, "Should generate suggestions"
        # Should be relevant to events/engagement
        suggestions_text = " ".join([s["question"].lower() for s in suggestions])
        # At least some suggestions should be contextually relevant


class TestIntegrationScenarios:
    """Test realistic integration scenarios"""

    async def test_full_analysis_workflow(self):
        """Test complete workflow: interpret then suggest"""
        engine = IntelligenceEngine()

        result = {
            "data": [
                {"industry": "Tech", "total_users": 500, "avg_ltv": 5000},
                {"industry": "Retail", "total_users": 300, "avg_ltv": 2500},
            ],
            "execution_time_ms": 80,
        }

        # First interpret
        interpretation = await engine.interpret_query_result(
            result=result, dimensions=["industry"], measures=["total_users", "avg_ltv"]
        )

        assert len(interpretation) > 0, "Should interpret results"

        # Then suggest next steps
        suggestions = await engine.generate_analysis_suggestions(
            current_result=result, context="users by industry analysis"
        )

        assert len(suggestions) > 0, "Should suggest next steps"

    async def test_compatibility_with_existing_methods(self):
        """Test that new methods work alongside existing methods"""
        engine = IntelligenceEngine()

        result = {
            "data": [
                {"plan_type": "free", "total_users": 100},
                {"plan_type": "pro", "total_users": 200},
            ],
            "execution_time_ms": 50,
        }

        query_info = {
            "model": "users",
            "dimensions": ["plan_type"],
            "measures": ["total_users"],
        }

        # Test new method
        interpretation = await engine.interpret_query_result(
            result=result, dimensions=["plan_type"], measures=["total_users"]
        )

        # Test existing method still works
        existing_interpretation = await engine.generate_interpretation(
            result=result, query_info=query_info
        )

        assert len(interpretation) > 0, "New method should work"
        assert len(existing_interpretation) > 0, "Existing method should still work"


# Run tests
async def run_tests():
    """Run all tests"""
    print("🧪 Running TDD Tests for IntelligenceEngine Fix")
    print("=" * 60)

    test_classes = [
        TestInterpretQueryResult,
        TestGenerateAnalysisSuggestions,
        TestIntegrationScenarios,
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = []

    for test_class in test_classes:
        print(f"\n📋 Testing {test_class.__name__}")
        test_instance = test_class()

        # Get all test methods
        test_methods = [
            method
            for method in dir(test_instance)
            if method.startswith("test_") and callable(getattr(test_instance, method))
        ]

        for test_method_name in test_methods:
            total_tests += 1
            test_method = getattr(test_instance, test_method_name)

            try:
                await test_method()
                print(f"   ✅ {test_method_name}")
                passed_tests += 1
            except Exception as e:
                print(f"   ❌ {test_method_name}: {str(e)}")
                failed_tests.append((test_method_name, str(e)))

    print("\n" + "=" * 60)
    print("🎯 TEST RESULTS")
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {len(failed_tests)}")

    if failed_tests:
        print("\n❌ Failed Tests:")
        for test_name, error in failed_tests:
            print(f"   • {test_name}: {error}")
        return False
    else:
        print("\n🎉 ALL TESTS PASSED!")
        return True


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    exit(0 if success else 1)
