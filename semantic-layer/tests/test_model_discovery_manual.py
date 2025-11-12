"""
Manual Model Discovery Test (No Network Required)

This test demonstrates the model discovery functionality without downloading
the SentenceTransformers model (which requires HuggingFace access).

To run with actual embeddings:
1. Ensure internet access to HuggingFace
2. Run: uv run python tests/test_model_discovery.py

This manual test validates:
1. Model loading from YAML files
2. Searchable text generation
3. Basic structure and caching
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_model_loading_without_embeddings():
    """Test that models can be loaded without embedding model"""
    from mcp_server.model_discovery import ModelDiscovery

    models_path = Path(__file__).parent.parent / "models"

    # Initialize with lazy loading (no embedder download)
    discovery = ModelDiscovery(models_path, lazy_load=True)

    print("✓ ModelDiscovery initialized successfully (lazy mode)")

    # Check that model configs are loaded
    assert len(discovery.model_configs) > 0, "No models loaded"
    print(f"✓ Loaded {len(discovery.model_configs)} model configurations")

    # Check expected models
    expected_models = {"users", "events", "engagement"}
    loaded_models = set(discovery.model_configs.keys())
    assert loaded_models == expected_models, f"Expected {expected_models}, got {loaded_models}"
    print(f"✓ Found expected models: {loaded_models}")

    # Check searchable descriptions were generated
    for model_name in loaded_models:
        assert model_name in discovery.model_descriptions
        assert len(discovery.model_descriptions[model_name]) > 0
        print(f"  - {model_name}: {len(discovery.model_descriptions[model_name])} chars")

    print("\n✓ All basic model loading tests passed!")


def test_model_metadata():
    """Test model metadata extraction"""
    from mcp_server.model_discovery import ModelDiscovery

    models_path = Path(__file__).parent.parent / "models"
    discovery = ModelDiscovery(models_path, lazy_load=True)

    # Test list_available_models
    models = discovery.list_available_models()
    print(f"\n✓ Available models: {len(models)}")

    for model in models:
        print(f"\n  Model: {model['name']}")
        print(f"    Description: {model['description'][:50]}...")
        print(f"    Table: {model['table']}")
        print(f"    Dimensions: {model['dimensions_count']}")
        print(f"    Measures: {model['measures_count']}")

    # Test get_model_summary
    users_summary = discovery.get_model_summary("users")
    assert users_summary is not None
    assert users_summary["name"] == "users"
    assert len(users_summary["dimensions"]) > 0
    assert len(users_summary["measures"]) > 0

    print(f"\n✓ Users model has {len(users_summary['dimensions'])} dimensions")
    print(f"✓ Users model has {len(users_summary['measures'])} measures")


def test_searchable_text_content():
    """Test that searchable text contains relevant keywords"""
    from mcp_server.model_discovery import ModelDiscovery

    models_path = Path(__file__).parent.parent / "models"
    discovery = ModelDiscovery(models_path, lazy_load=True)

    # Test users model
    users_text = discovery.model_descriptions["users"]
    assert "user" in users_text.lower()
    assert "conversion" in users_text.lower()
    assert "plan_type" in users_text.lower()
    print("\n✓ Users model contains expected keywords")

    # Test events model
    events_text = discovery.model_descriptions["events"]
    assert "event" in events_text.lower()
    assert "feature" in events_text.lower()
    assert "adoption" in events_text.lower()
    print("✓ Events model contains expected keywords")

    # Test engagement model
    engagement_text = discovery.model_descriptions["engagement"]
    assert "engagement" in engagement_text.lower()
    assert "retention" in engagement_text.lower()
    assert "dau" in engagement_text.lower() or "daily active" in engagement_text.lower()
    print("✓ Engagement model contains expected keywords")


def demonstrate_expected_behavior():
    """
    Demonstrate what the model discovery would do with embeddings.

    This shows the expected workflow without actually running embeddings.
    """
    print("\n" + "="*80)
    print("EXPECTED MODEL DISCOVERY BEHAVIOR (With Embeddings)")
    print("="*80)

    test_questions = [
        ("What's our revenue?", ["users", "events"]),
        ("Show me user churn", ["engagement", "users"]),
        ("Feature adoption rates", ["events"]),
        ("Daily active users", ["engagement"]),
        ("Conversion rate by industry", ["users"]),
    ]

    print("\nTest Questions and Expected Top Models:")
    print("-" * 80)
    for question, expected_models in test_questions:
        print(f"\nQ: '{question}'")
        print(f"   Expected: {', '.join(expected_models)}")
        print(f"   Rationale: Question contains keywords relevant to these models")

    print("\n" + "="*80)
    print("ACCURACY VALIDATION")
    print("="*80)
    print("\nWith actual embeddings, the system should achieve:")
    print("- 85%+ accuracy in selecting correct model")
    print("- <100ms search time per query")
    print("- Offline operation (no API calls after initial download)")
    print("- Lightweight (33MB model size)")


if __name__ == "__main__":
    print("="*80)
    print("MODEL DISCOVERY MANUAL TESTS")
    print("="*80)

    try:
        test_model_loading_without_embeddings()
        test_model_metadata()
        test_searchable_text_content()
        demonstrate_expected_behavior()

        print("\n" + "="*80)
        print("✅ ALL MANUAL TESTS PASSED")
        print("="*80)
        print("\nNote: Full embedding tests require HuggingFace access.")
        print("To run with actual embeddings:")
        print("  1. Ensure internet access to huggingface.co")
        print("  2. Run: uv run python tests/test_model_discovery.py")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
