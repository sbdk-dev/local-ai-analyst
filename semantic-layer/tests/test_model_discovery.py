"""
Tests for RAG Model Discovery System

Tests:
1. Embedding generation for all models
2. Vector similarity search
3. Accuracy on test questions (target: 85%+)
4. Performance (<100ms search time)
"""

import asyncio
import time
from pathlib import Path
import pytest
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.model_discovery import ModelDiscovery


@pytest.fixture
def models_path():
    """Path to semantic models"""
    return Path(__file__).parent.parent / "models"


@pytest.fixture
async def discovery(models_path):
    """Initialize ModelDiscovery instance"""
    return ModelDiscovery(models_path)


class TestEmbeddingGeneration:
    """Test embedding generation for semantic models"""

    @pytest.mark.asyncio
    async def test_models_loaded(self, discovery):
        """Test that all models are loaded and embedded"""
        expected_models = {"users", "events", "engagement"}
        loaded_models = set(discovery.model_embeddings.keys())

        assert loaded_models == expected_models, f"Expected {expected_models}, got {loaded_models}"

    @pytest.mark.asyncio
    async def test_embeddings_are_vectors(self, discovery):
        """Test that embeddings are numpy arrays with correct dimensions"""
        for model_name, embedding in discovery.model_embeddings.items():
            assert embedding is not None, f"Embedding for {model_name} is None"
            assert len(embedding.shape) == 1, f"Embedding for {model_name} should be 1D vector"
            assert embedding.shape[0] == 384, f"Embedding should be 384-dimensional (all-MiniLM-L6-v2)"

    @pytest.mark.asyncio
    async def test_model_descriptions_exist(self, discovery):
        """Test that all models have searchable descriptions"""
        for model_name in discovery.model_embeddings.keys():
            assert model_name in discovery.model_descriptions
            assert len(discovery.model_descriptions[model_name]) > 0


class TestSimilaritySearch:
    """Test vector similarity search functionality"""

    @pytest.mark.asyncio
    async def test_discover_models_returns_results(self, discovery):
        """Test that discover_models returns ranked results"""
        results = await discovery.discover_models("What's our revenue?", top_k=3)

        assert len(results) > 0, "Should return at least one model"
        assert len(results) <= 3, "Should respect top_k limit"

    @pytest.mark.asyncio
    async def test_results_have_required_fields(self, discovery):
        """Test that results have model, similarity, and description"""
        results = await discovery.discover_models("How many users?", top_k=2)

        for result in results:
            assert "model" in result
            assert "similarity" in result
            assert "description" in result
            assert 0.0 <= result["similarity"] <= 1.0, "Similarity should be between 0 and 1"

    @pytest.mark.asyncio
    async def test_results_are_sorted_by_similarity(self, discovery):
        """Test that results are sorted in descending order of similarity"""
        results = await discovery.discover_models("User engagement metrics", top_k=3)

        similarities = [r["similarity"] for r in results]
        assert similarities == sorted(similarities, reverse=True), "Results should be sorted by similarity"

    @pytest.mark.asyncio
    async def test_similarity_threshold_filtering(self, discovery):
        """Test that similarity threshold filters low-confidence results"""
        # Use high threshold
        results_high = await discovery.discover_models(
            "xyz random nonsense query",
            top_k=3,
            similarity_threshold=0.8
        )

        # Use low threshold
        results_low = await discovery.discover_models(
            "xyz random nonsense query",
            top_k=3,
            similarity_threshold=0.0
        )

        # High threshold should return fewer or equal results
        assert len(results_high) <= len(results_low)


class TestAccuracy:
    """Test accuracy on specific test questions (target: 85%+)"""

    # Test cases with expected top model
    TEST_QUESTIONS = [
        # Revenue questions → should find events or users (both have revenue-related measures)
        {
            "question": "What's our revenue this month?",
            "expected_top_models": ["users", "events"],  # Both valid
            "expected_min_similarity": 0.3
        },
        {
            "question": "Show me total revenue",
            "expected_top_models": ["users", "events"],
            "expected_min_similarity": 0.3
        },

        # User questions → should find users model
        {
            "question": "How many users signed up last week?",
            "expected_top_models": ["users"],
            "expected_min_similarity": 0.5
        },
        {
            "question": "What's our user count by plan type?",
            "expected_top_models": ["users"],
            "expected_min_similarity": 0.5
        },
        {
            "question": "Show me conversion rate",
            "expected_top_models": ["users"],
            "expected_min_similarity": 0.4
        },
        {
            "question": "User demographics by industry",
            "expected_top_models": ["users"],
            "expected_min_similarity": 0.5
        },

        # Event/Feature questions → should find events model
        {
            "question": "What features do users use most?",
            "expected_top_models": ["events"],
            "expected_min_similarity": 0.5
        },
        {
            "question": "Show me feature adoption rates",
            "expected_top_models": ["events"],
            "expected_min_similarity": 0.5
        },
        {
            "question": "Which features are most popular?",
            "expected_top_models": ["events"],
            "expected_min_similarity": 0.5
        },
        {
            "question": "Login event counts",
            "expected_top_models": ["events"],
            "expected_min_similarity": 0.4
        },

        # Engagement questions → should find engagement model
        {
            "question": "What's our daily active users?",
            "expected_top_models": ["engagement"],
            "expected_min_similarity": 0.5
        },
        {
            "question": "Show me DAU/MAU ratio",
            "expected_top_models": ["engagement"],
            "expected_min_similarity": 0.6
        },
        {
            "question": "User retention analysis",
            "expected_top_models": ["engagement"],
            "expected_min_similarity": 0.5
        },
        {
            "question": "How sticky is our product?",
            "expected_top_models": ["engagement"],
            "expected_min_similarity": 0.4
        },
        {
            "question": "Cohort retention rates",
            "expected_top_models": ["engagement"],
            "expected_min_similarity": 0.5
        },
    ]

    @pytest.mark.asyncio
    async def test_individual_question_accuracy(self, discovery):
        """Test accuracy for each individual question"""
        results = []

        for test_case in self.TEST_QUESTIONS:
            question = test_case["question"]
            expected_models = test_case["expected_top_models"]
            min_similarity = test_case["expected_min_similarity"]

            # Get top result
            discovered = await discovery.discover_models(question, top_k=1)

            if not discovered:
                results.append({
                    "question": question,
                    "expected": expected_models,
                    "actual": None,
                    "similarity": 0.0,
                    "passed": False
                })
                continue

            top_model = discovered[0]["model"]
            top_similarity = discovered[0]["similarity"]

            # Check if top model matches expected and meets min similarity
            passed = (top_model in expected_models) and (top_similarity >= min_similarity)

            results.append({
                "question": question,
                "expected": expected_models,
                "actual": top_model,
                "similarity": top_similarity,
                "passed": passed
            })

        # Calculate accuracy
        passed_count = sum(1 for r in results if r["passed"])
        total_count = len(results)
        accuracy = passed_count / total_count if total_count > 0 else 0.0

        # Print detailed results
        print("\n" + "="*80)
        print("MODEL DISCOVERY ACCURACY TEST RESULTS")
        print("="*80)
        for r in results:
            status = "✓" if r["passed"] else "✗"
            print(f"\n{status} Q: {r['question']}")
            print(f"  Expected: {r['expected']}")
            print(f"  Got: {r['actual']} (similarity: {r['similarity']:.3f})")

        print("\n" + "="*80)
        print(f"ACCURACY: {passed_count}/{total_count} = {accuracy:.1%}")
        print("="*80)

        # Assert 85%+ accuracy
        assert accuracy >= 0.85, f"Accuracy {accuracy:.1%} is below 85% threshold"

    @pytest.mark.asyncio
    async def test_revenue_questions(self, discovery):
        """Test revenue-related questions"""
        revenue_questions = [
            "What's our revenue?",
            "Show me total revenue",
            "Revenue by plan type"
        ]

        for question in revenue_questions:
            results = await discovery.discover_models(question, top_k=1)
            assert len(results) > 0, f"No results for: {question}"
            # Revenue could be in users or events model
            assert results[0]["model"] in ["users", "events"]

    @pytest.mark.asyncio
    async def test_user_churn_questions(self, discovery):
        """Test user churn questions → should find engagement or users"""
        churn_questions = [
            "Show me user churn",
            "What's our churn rate?",
            "User retention over time"
        ]

        for question in churn_questions:
            results = await discovery.discover_models(question, top_k=1)
            assert len(results) > 0, f"No results for: {question}"
            # Churn/retention is in engagement model
            assert results[0]["model"] in ["engagement", "users"]


class TestPerformance:
    """Test performance requirements (<100ms search time)"""

    @pytest.mark.asyncio
    async def test_search_performance(self, discovery):
        """Test that search completes in <100ms"""
        test_questions = [
            "What's our revenue?",
            "Show me user churn",
            "Feature adoption rates",
            "Daily active users"
        ]

        timings = []

        for question in test_questions:
            start = time.perf_counter()
            results = await discovery.discover_models(question, top_k=3)
            elapsed_ms = (time.perf_counter() - start) * 1000

            timings.append({
                "question": question,
                "time_ms": elapsed_ms,
                "passed": elapsed_ms < 100
            })

            assert len(results) > 0, f"No results for: {question}"

        # Print performance results
        print("\n" + "="*80)
        print("MODEL DISCOVERY PERFORMANCE TEST RESULTS")
        print("="*80)
        for t in timings:
            status = "✓" if t["passed"] else "✗"
            print(f"{status} {t['question']}: {t['time_ms']:.1f}ms")

        avg_time = sum(t["time_ms"] for t in timings) / len(timings)
        print(f"\nAverage search time: {avg_time:.1f}ms")
        print("="*80)

        # All searches should be <100ms
        for t in timings:
            assert t["passed"], f"Search took {t['time_ms']:.1f}ms (>100ms): {t['question']}"

    @pytest.mark.asyncio
    async def test_initialization_performance(self, models_path):
        """Test that initialization (loading + embedding) is reasonable"""
        start = time.perf_counter()
        discovery = ModelDiscovery(models_path)
        elapsed_ms = (time.perf_counter() - start) * 1000

        print(f"\nInitialization time: {elapsed_ms:.1f}ms")

        # Initialization can be slower (first time downloads model)
        # But should be reasonable (<5 seconds)
        assert elapsed_ms < 5000, f"Initialization took {elapsed_ms:.1f}ms (>5s)"


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_empty_query(self, discovery):
        """Test handling of empty query"""
        results = await discovery.discover_models("", top_k=3)
        # Should still return results (empty query has some embedding)
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_very_long_query(self, discovery):
        """Test handling of very long query"""
        long_query = "revenue " * 100  # 100-word repetition
        results = await discovery.discover_models(long_query, top_k=3)
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_top_k_larger_than_models(self, discovery):
        """Test requesting more results than available models"""
        results = await discovery.discover_models("user data", top_k=100)
        # Should return all available models (3)
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_zero_top_k(self, discovery):
        """Test requesting zero results"""
        results = await discovery.discover_models("user data", top_k=0)
        assert len(results) == 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
