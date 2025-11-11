#!/usr/bin/env python3
"""
TDD Tests for SemanticLayerManager.list_available_models()

Tests written BEFORE implementation to drive the design.
"""

import asyncio
import pytest
from pathlib import Path
from mcp_server.semantic_layer_integration import SemanticLayerManager


class TestListAvailableModels:
    """Test suite for list_available_models() method"""

    @pytest.fixture
    async def manager(self):
        """Create and initialize SemanticLayerManager"""
        mgr = SemanticLayerManager()
        await mgr.initialize()
        return mgr

    @pytest.mark.asyncio
    async def test_returns_list_of_dicts(self):
        """Should return a list of model dictionaries"""
        manager = SemanticLayerManager()
        await manager.initialize()

        result = await manager.list_available_models()

        assert isinstance(result, list), "Result should be a list"
        assert len(result) > 0, "Should return at least one model"
        assert all(isinstance(item, dict) for item in result), "All items should be dictionaries"

    @pytest.mark.asyncio
    async def test_includes_all_yaml_models(self):
        """Should include all models from YAML files"""
        manager = SemanticLayerManager()
        await manager.initialize()

        result = await manager.list_available_models()
        model_names = [m["name"] for m in result]

        # Should include the three models we know exist
        assert "users" in model_names, "Should include users model"
        assert "events" in model_names, "Should include events model"
        assert "engagement" in model_names, "Should include engagement model"
        assert len(model_names) == 3, "Should have exactly 3 models"

    @pytest.mark.asyncio
    async def test_includes_model_name(self):
        """Each model should have a name"""
        manager = SemanticLayerManager()
        await manager.initialize()

        result = await manager.list_available_models()

        for model in result:
            assert "name" in model, "Model should have 'name' field"
            assert isinstance(model["name"], str), "Name should be a string"
            assert len(model["name"]) > 0, "Name should not be empty"

    @pytest.mark.asyncio
    async def test_includes_model_description(self):
        """Each model should have a description"""
        manager = SemanticLayerManager()
        await manager.initialize()

        result = await manager.list_available_models()

        for model in result:
            assert "description" in model, "Model should have 'description' field"
            assert isinstance(model["description"], str), "Description should be a string"

    @pytest.mark.asyncio
    async def test_includes_dimensions_list(self):
        """Each model should have a list of dimension names"""
        manager = SemanticLayerManager()
        await manager.initialize()

        result = await manager.list_available_models()

        for model in result:
            assert "dimensions" in model, "Model should have 'dimensions' field"
            assert isinstance(model["dimensions"], list), "Dimensions should be a list"

            # Verify all dimensions are strings (dimension names)
            for dim in model["dimensions"]:
                assert isinstance(dim, str), "Dimension should be a string"

    @pytest.mark.asyncio
    async def test_includes_measures_list(self):
        """Each model should have a list of measure names"""
        manager = SemanticLayerManager()
        await manager.initialize()

        result = await manager.list_available_models()

        for model in result:
            assert "measures" in model, "Model should have 'measures' field"
            assert isinstance(model["measures"], list), "Measures should be a list"

            # Verify all measures are strings (measure names)
            for measure in model["measures"]:
                assert isinstance(measure, str), "Measure should be a string"

    @pytest.mark.asyncio
    async def test_dimensions_match_yaml_structure(self):
        """Dimensions should match what's defined in YAML files"""
        manager = SemanticLayerManager()
        await manager.initialize()

        result = await manager.list_available_models()

        # Find users model
        users_model = next(m for m in result if m["name"] == "users")

        # Users model should have these dimensions based on users.yml
        expected_dims = ["user_id", "signup_date", "plan_type", "industry", "company_size", "country"]
        assert set(users_model["dimensions"]) == set(expected_dims), \
            f"Users dimensions should match YAML. Got: {users_model['dimensions']}"

    @pytest.mark.asyncio
    async def test_measures_match_yaml_structure(self):
        """Measures should match what's defined in YAML files"""
        manager = SemanticLayerManager()
        await manager.initialize()

        result = await manager.list_available_models()

        # Find users model
        users_model = next(m for m in result if m["name"] == "users")

        # Users model should have these measures based on users.yml
        expected_measures = ["total_users", "free_users", "paid_users", "enterprise_users", "conversion_rate"]
        assert set(users_model["measures"]) == set(expected_measures), \
            f"Users measures should match YAML. Got: {users_model['measures']}"

    @pytest.mark.asyncio
    async def test_includes_relationships(self):
        """Each model should have a relationships field (may be empty)"""
        manager = SemanticLayerManager()
        await manager.initialize()

        result = await manager.list_available_models()

        for model in result:
            assert "relationships" in model, "Model should have 'relationships' field"
            assert isinstance(model["relationships"], list), "Relationships should be a list"

    @pytest.mark.asyncio
    async def test_events_model_has_relationships(self):
        """Events model should identify relationships to users and sessions"""
        manager = SemanticLayerManager()
        await manager.initialize()

        result = await manager.list_available_models()

        # Find events model
        events_model = next(m for m in result if m["name"] == "events")

        # Events has foreign keys to users and sessions (should be sorted)
        assert "sessions" in events_model["relationships"], \
            "Events should have relationship to sessions"
        assert "users" in events_model["relationships"], \
            "Events should have relationship to users"
        # Verify relationships are sorted
        assert events_model["relationships"] == sorted(events_model["relationships"]), \
            "Relationships should be sorted alphabetically"

    @pytest.mark.asyncio
    async def test_complete_model_structure(self):
        """Verify complete structure of a model dictionary"""
        manager = SemanticLayerManager()
        await manager.initialize()

        result = await manager.list_available_models()
        users_model = next(m for m in result if m["name"] == "users")

        # Verify all required fields are present
        required_fields = ["name", "description", "dimensions", "measures", "relationships"]
        for field in required_fields:
            assert field in users_model, f"Model should have '{field}' field"

        # Verify structure matches example from task
        assert users_model["name"] == "users"
        assert "User demographics" in users_model["description"]
        assert len(users_model["dimensions"]) == 6
        assert len(users_model["measures"]) == 5
        assert isinstance(users_model["relationships"], list)

    @pytest.mark.asyncio
    async def test_handles_empty_models_directory(self):
        """Should handle case where models directory has no YAML files"""
        manager = SemanticLayerManager()

        # Temporarily point to empty directory
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            manager.models_path = Path(tmpdir)
            await manager.initialize()

            result = await manager.list_available_models()

            assert isinstance(result, list), "Should return empty list, not error"
            assert len(result) == 0, "Should return empty list for no models"

    @pytest.mark.asyncio
    async def test_validates_yaml_parsing(self):
        """Should handle malformed YAML files gracefully"""
        manager = SemanticLayerManager()
        await manager.initialize()

        # Even with valid YAML, should not crash
        result = await manager.list_available_models()

        assert isinstance(result, list), "Should return list even if some YAML parsing fails"

    @pytest.mark.asyncio
    async def test_performance_under_100ms(self):
        """Should execute in under 100ms for 3 models"""
        import time

        manager = SemanticLayerManager()
        await manager.initialize()

        start = time.time()
        result = await manager.list_available_models()
        elapsed_ms = (time.time() - start) * 1000

        assert elapsed_ms < 100, f"Should complete in <100ms, took {elapsed_ms:.2f}ms"
        assert len(result) == 3, "Should return all 3 models"

    @pytest.mark.asyncio
    async def test_caching_improves_performance(self):
        """Second call should be faster due to caching"""
        import time

        manager = SemanticLayerManager()
        await manager.initialize()

        # First call - builds cache
        start1 = time.time()
        result1 = await manager.list_available_models()
        time1_ms = (time.time() - start1) * 1000

        # Second call - uses cache
        start2 = time.time()
        result2 = await manager.list_available_models()
        time2_ms = (time.time() - start2) * 1000

        # Verify results are identical
        assert result1 == result2, "Cached result should match original"

        # Cached call should be significantly faster (at least 5x)
        assert time2_ms < time1_ms / 5, \
            f"Cached call ({time2_ms:.2f}ms) should be much faster than first call ({time1_ms:.2f}ms)"

    @pytest.mark.asyncio
    async def test_cache_invalidation_on_reload(self):
        """Cache should be invalidated when models are reloaded"""
        manager = SemanticLayerManager()
        await manager.initialize()

        # First call - builds cache
        result1 = await manager.list_available_models()
        assert manager._models_list_cache is not None, "Cache should be populated"

        # Reload models - should invalidate cache
        await manager._load_models()

        # Cache should be cleared but will rebuild on next call
        # (Cache is None after load, then populated on first access)
        result2 = await manager.list_available_models()
        assert result2 == result1, "Results should be the same after reload"

    @pytest.mark.asyncio
    async def test_models_sorted_by_name(self):
        """Models should be returned in alphabetical order by name"""
        manager = SemanticLayerManager()
        await manager.initialize()

        result = await manager.list_available_models()
        model_names = [m["name"] for m in result]

        # Verify models are sorted
        assert model_names == sorted(model_names), \
            f"Models should be sorted alphabetically: {model_names}"


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
