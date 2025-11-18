"""
RAG Model Discovery System

Discovers relevant semantic models using vector similarity search.
Uses lightweight SentenceTransformers (no external vector DB needed).

Target Performance:
- 85%+ accuracy in model selection
- <100ms search time
- Works offline (no API calls)
- Lightweight (33MB model)
"""

import json
import logging
import numpy as np
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import yaml

logger = logging.getLogger(__name__)


class ModelDiscovery:
    """
    Discover relevant semantic models using vector similarity search.

    Features:
    - Lightweight SentenceTransformers (no external vector DB)
    - Embeddings cached locally for fast lookup
    - Natural language model selection
    - Offline operation
    """

    def __init__(self, models_path: Path, lazy_load: bool = False):
        """
        Initialize ModelDiscovery with semantic models.

        Args:
            models_path: Path to directory containing semantic model YAML files
            lazy_load: If True, delay loading embedder until first use (default: False)
        """
        self.models_path = Path(models_path)

        # Lazy-loaded embedder (initialized on first use)
        self.embedder = None
        self._lazy_load = lazy_load

        # Cache: {model_name: embedding_vector}
        self.model_embeddings: Dict[str, np.ndarray] = {}

        # Cache: {model_name: searchable_text}
        self.model_descriptions: Dict[str, str] = {}

        # Cache: {model_name: model_config}
        self.model_configs: Dict[str, Dict[str, Any]] = {}

        # Load model configs (always, even in lazy mode)
        self._load_model_configs()

        # Embed models (unless lazy loading)
        if not lazy_load:
            self._ensure_embedder_loaded()
            self._embed_models()

    def _ensure_embedder_loaded(self):
        """Ensure the embedding model is loaded (lazy initialization)"""
        if self.embedder is None:
            # Lazy import to avoid loading at module level
            from sentence_transformers import SentenceTransformer

            # Use small, fast embedding model (33MB, CPU-friendly)
            # all-MiniLM-L6-v2: 384-dimensional embeddings
            logger.info("Loading embedding model: all-MiniLM-L6-v2")
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model loaded successfully")

    def _load_model_configs(self):
        """Load semantic model configurations from YAML files"""

        model_files = list(self.models_path.glob("*.yml"))
        logger.info(f"Found {len(model_files)} model files in {self.models_path}")

        for model_file in model_files:
            try:
                with open(model_file, "r") as f:
                    model_config = yaml.safe_load(f)

                model_name = model_config["model"]["name"]

                # Build searchable description from all model metadata
                searchable_text = self._build_searchable_text(model_config)

                # Cache model config and searchable text
                self.model_configs[model_name] = model_config
                self.model_descriptions[model_name] = searchable_text

                logger.info(f"Loaded model config: {model_name} ({len(searchable_text)} chars)")

            except Exception as e:
                logger.error(f"Failed to load model {model_file}: {e}")

        logger.info(f"Successfully loaded {len(self.model_configs)} model configurations")

    def _embed_models(self):
        """Create embeddings for all loaded models"""

        if not self.model_configs:
            logger.warning("No model configs loaded, cannot create embeddings")
            return

        logger.info(f"Creating embeddings for {len(self.model_configs)} models")

        for model_name, searchable_text in self.model_descriptions.items():
            try:
                # Create embedding
                embedding = self.embedder.encode(searchable_text, convert_to_numpy=True)

                # Cache embedding
                self.model_embeddings[model_name] = embedding

                logger.info(f"Embedded model: {model_name}")

            except Exception as e:
                logger.error(f"Failed to embed model {model_name}: {e}")

        logger.info(f"Successfully created embeddings for {len(self.model_embeddings)} models")

    def _build_searchable_text(self, model_config: Dict[str, Any]) -> str:
        """
        Build searchable text from model configuration.

        Includes:
        - Model description
        - Table name
        - Dimension names and descriptions
        - Measure names and descriptions
        - Context metadata
        """
        parts = []

        # Model description
        model_info = model_config.get("model", {})
        if "description" in model_info:
            parts.append(model_info["description"])

        # Table name
        if "table" in model_info:
            parts.append(f"Table: {model_info['table']}")

        # Dimensions
        for dim in model_config.get("dimensions", []):
            dim_text = f"Dimension: {dim['name']}"
            if "description" in dim:
                dim_text += f" - {dim['description']}"
            parts.append(dim_text)

        # Measures
        for measure in model_config.get("measures", []):
            measure_text = f"Measure: {measure['name']}"
            if "description" in measure:
                measure_text += f" - {measure['description']}"
            parts.append(measure_text)

        # Time series measures (if present)
        for measure in model_config.get("time_series_measures", []):
            measure_text = f"Time Series Measure: {measure['name']}"
            if "description" in measure:
                measure_text += f" - {measure['description']}"
            parts.append(measure_text)

        # Feature measures (if present)
        for measure in model_config.get("feature_measures", []):
            measure_text = f"Feature Measure: {measure['name']}"
            if "description" in measure:
                measure_text += f" - {measure['description']}"
            parts.append(measure_text)

        # Context metadata
        context = model_config.get("context", {})

        # Benchmarks
        for benchmark in context.get("benchmarks", []):
            if "metric" in benchmark:
                parts.append(f"Benchmark metric: {benchmark['metric']}")

        # Feature importance (for events model)
        feature_importance = context.get("feature_importance", {})
        for category, features in feature_importance.items():
            if isinstance(features, list):
                parts.append(f"{category}: {', '.join(features)}")

        # Interpretations
        for metric, interpretation in context.get("interpretations", {}).items():
            parts.append(f"Metric: {metric}")

        # Sample queries
        for sample_query in model_config.get("sample_queries", []):
            if "description" in sample_query:
                parts.append(f"Query: {sample_query['description']}")

        # Auto insights
        for insight in model_config.get("auto_insights", []):
            if "description" in insight:
                parts.append(f"Insight: {insight['description']}")

        # Validation patterns
        validation = model_config.get("validation", {})
        for pattern_list in validation.values():
            if isinstance(pattern_list, list):
                for pattern in pattern_list:
                    if isinstance(pattern, dict) and "check" in pattern:
                        parts.append(f"Analysis: {pattern['check']}")

        # Combine all parts
        searchable_text = " ".join(filter(None, parts))

        return searchable_text

    async def discover_models(
        self,
        user_question: str,
        top_k: int = 3,
        similarity_threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Find relevant models for user question using vector similarity.

        Args:
            user_question: User's natural language question
            top_k: Number of models to return (default: 3)
            similarity_threshold: Minimum similarity score 0-1 (default: 0.3)

        Returns:
            List of models with similarity scores, sorted by relevance

        Example:
            >>> results = await discovery.discover_models("What's our revenue?", top_k=2)
            >>> results[0]
            {
                "model": "users",
                "similarity": 0.85,
                "description": "User demographics, signup information..."
            }
        """

        # Ensure embedder is loaded (lazy loading support)
        self._ensure_embedder_loaded()

        # Ensure models are embedded (if not already done)
        if not self.model_embeddings:
            self._embed_models()

        # Handle empty query
        if not user_question or not user_question.strip():
            logger.warning("Empty question provided to discover_models")
            user_question = "data"  # Fallback

        # Embed user question
        question_embedding = self.embedder.encode(user_question, convert_to_numpy=True)

        # Calculate similarities with all models
        similarities = []
        for model_name, model_embedding in self.model_embeddings.items():
            # Cosine similarity
            similarity = self._cosine_similarity(question_embedding, model_embedding)

            similarities.append({
                "model": model_name,
                "similarity": float(similarity),
                "description": self.model_descriptions[model_name][:200]  # Truncate for display
            })

        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x["similarity"], reverse=True)

        # Filter by threshold and limit to top_k
        results = [
            s for s in similarities
            if s["similarity"] >= similarity_threshold
        ][:top_k]

        logger.info(
            f"Question: '{user_question[:50]}...' -> "
            f"Top model: {results[0]['model'] if results else 'none'} "
            f"({results[0]['similarity']:.3f})" if results else "no results"
        )

        return results

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.

        Formula: cos(θ) = (A · B) / (||A|| * ||B||)

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Similarity score between 0 and 1 (1 = identical, 0 = orthogonal)
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get full configuration for a model.

        Args:
            model_name: Name of the model

        Returns:
            Model configuration dict or None if not found
        """
        return self.model_configs.get(model_name)

    async def suggest_dimensions_and_measures(
        self,
        user_question: str,
        model_name: str
    ) -> Dict[str, List[str]]:
        """
        Suggest relevant dimensions and measures for a model based on question.

        This is a future enhancement placeholder. Currently returns empty suggestions.

        Future implementation could use:
        - Entity extraction from question
        - Embedding similarity on individual dimensions/measures
        - Pattern matching on common question types

        Args:
            user_question: User's natural language question
            model_name: Target semantic model

        Returns:
            Dict with suggested dimensions and measures

        Example:
            Q: "What's revenue by industry?"
            Model: "users"
            Returns: {
                "dimensions": ["industry"],
                "measures": ["total_revenue"],
                "confidence": 0.85
            }
        """

        # Placeholder for future enhancement
        # Could implement by:
        # 1. Extract entities from question (industry, plan_type, etc.)
        # 2. Embed dimension/measure descriptions
        # 3. Match question keywords to dimensions/measures
        # 4. Return top matches with confidence scores

        return {
            "dimensions": [],
            "measures": [],
            "confidence": 0.0,
            "note": "Dimension/measure suggestion not yet implemented"
        }

    def list_available_models(self) -> List[Dict[str, str]]:
        """
        List all available models with descriptions.

        Returns:
            List of models with names and descriptions
        """
        models = []
        for model_name, config in self.model_configs.items():
            models.append({
                "name": model_name,
                "description": config["model"].get("description", ""),
                "table": config["model"].get("table", ""),
                "dimensions_count": len(config.get("dimensions", [])),
                "measures_count": len(config.get("measures", []))
            })

        return sorted(models, key=lambda x: x["name"])

    def get_model_summary(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get summary information for a specific model.

        Args:
            model_name: Name of the model

        Returns:
            Summary dict or None if model not found
        """
        config = self.model_configs.get(model_name)
        if not config:
            return None

        model_info = config.get("model", {})

        return {
            "name": model_name,
            "description": model_info.get("description", ""),
            "table": model_info.get("table", ""),
            "dimensions": [
                {
                    "name": d["name"],
                    "type": d.get("type", "unknown"),
                    "description": d.get("description", "")
                }
                for d in config.get("dimensions", [])
            ],
            "measures": [
                {
                    "name": m["name"],
                    "type": m.get("type", "unknown"),
                    "description": m.get("description", "")
                }
                for m in config.get("measures", [])
            ]
        }
