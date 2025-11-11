# WrenAI Reusable Components for Claude-Analyst

**Research Date**: 2025-11-11  
**Purpose**: Concrete integration recommendations with code examples  
**Status**: Ready for Implementation  

---

## Executive Summary

This document identifies specific WrenAI patterns and components that can be adopted by claude-analyst, with **clean-room implementations** to avoid AGPL-3.0 license contamination. Each component includes:

- **Rationale**: Why adopt this pattern
- **Implementation**: Concrete Python code examples
- **Integration Points**: Where it fits in claude-analyst
- **Testing Strategy**: How to validate it works
- **Estimated Effort**: Time to implement

---

## Component Matrix: Adopt, Adapt, or Avoid

| Component | Decision | Priority | Effort | Impact |
|-----------|----------|----------|--------|--------|
| SQL Dry-Run Validation | ✅ Adopt | P1 | 1 week | High |
| RAG Model Discovery | ✅ Adopt | P1 | 1 week | High |
| Runtime Metric Definitions | ✅ Adopt | P1 | 1 week | High |
| Visualization Layer | ✅ Adopt | P2 | 1 week | Medium |
| Multi-Database Support | ✅ Adopt | P2 | 2 weeks | Medium |
| DAG Pipeline (Haystack+Hamilton) | ⚠️ Adapt | P3 | 2 weeks | Low |
| MDL JSON Format | ⚠️ Adapt | P3 | 1 week | Low |
| Error Correction Loop | ❌ Avoid | - | - | - |

**Legend**:
- ✅ **Adopt**: Implement clean-room version
- ⚠️ **Adapt**: Use pattern, different implementation
- ❌ **Avoid**: Not needed or conflicts with design

---

## Priority 1: High-Impact Components

### 1. SQL Dry-Run Validation

**Rationale**:
- Catch query errors before expensive execution
- Provide better error messages to users
- Prevent resource exhaustion from bad queries
- **Gap in claude-analyst**: We rely on Ibis type safety but lack runtime validation

**WrenAI Pattern**:
```python
# WrenAI approach (conceptual, not actual code)
validation_result = engine.dry_run(sql)
if not validation_result.valid:
    corrected_sql = llm.correct(sql, validation_result.error)
```

**Claude-Analyst Implementation** (Clean-Room):

```python
# File: semantic-layer/mcp_server/query_validator.py

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of query validation"""
    valid: bool
    error: Optional[str] = None
    warnings: list[str] = None
    estimated_rows: Optional[int] = None
    estimated_time_ms: Optional[float] = None
    complexity_score: float = 0.0  # 0-100, higher = more complex


class QueryValidator:
    """
    Validates queries before execution to catch errors early.
    
    Validation Steps:
    1. Dry-run with LIMIT 0 (no data fetched)
    2. Complexity analysis (joins, aggregations)
    3. Result size estimation
    4. Resource impact prediction
    """
    
    def __init__(self, connection):
        self.connection = connection
        self.max_complexity = 80.0
        self.max_estimated_rows = 100_000
        
    async def validate_ibis_query(
        self, 
        ibis_expr, 
        query_info: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate Ibis query expression before execution.
        
        Args:
            ibis_expr: Ibis query expression
            query_info: Query metadata (model, dimensions, measures)
            
        Returns:
            ValidationResult with validation status and insights
        """
        try:
            # Step 1: Compile to SQL
            sql = ibis_expr.compile()
            
            # Step 2: Dry-run validation (EXPLAIN instead of execution)
            try:
                explain_result = self.connection.sql(f"EXPLAIN {sql}").to_pandas()
                
                # Extract query plan information
                plan_text = explain_result.iloc[0, 0] if not explain_result.empty else ""
                
            except Exception as e:
                return ValidationResult(
                    valid=False,
                    error=f"Query validation failed: {str(e)}",
                    warnings=[]
                )
            
            # Step 3: Analyze complexity
            complexity = self._analyze_complexity(sql, query_info)
            
            if complexity > self.max_complexity:
                return ValidationResult(
                    valid=False,
                    error=f"Query too complex (score: {complexity}). Consider adding filters or reducing dimensions.",
                    complexity_score=complexity
                )
            
            # Step 4: Estimate result size
            estimated_rows = await self._estimate_result_size(sql, query_info)
            
            if estimated_rows > self.max_estimated_rows:
                return ValidationResult(
                    valid=False,
                    error=f"Result too large ({estimated_rows:,} estimated rows). Add LIMIT or filters.",
                    estimated_rows=estimated_rows
                )
            
            # Step 5: Check for common issues
            warnings = self._check_for_warnings(sql, query_info)
            
            # All checks passed
            return ValidationResult(
                valid=True,
                warnings=warnings,
                estimated_rows=estimated_rows,
                complexity_score=complexity
            )
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return ValidationResult(
                valid=False,
                error=f"Validation error: {str(e)}"
            )
    
    def _analyze_complexity(self, sql: str, query_info: Dict[str, Any]) -> float:
        """
        Calculate query complexity score (0-100).
        
        Factors:
        - Number of dimensions (each adds 5)
        - Number of measures (each adds 3)
        - Number of JOINs (each adds 10)
        - Subqueries (each adds 15)
        - DISTINCT operations (adds 5)
        """
        complexity = 10.0  # Base complexity
        
        # Dimension complexity
        dimensions = len(query_info.get("dimensions", []))
        complexity += dimensions * 5
        
        # Measure complexity
        measures = len(query_info.get("measures", []))
        complexity += measures * 3
        
        # JOIN complexity
        join_count = sql.upper().count("JOIN")
        complexity += join_count * 10
        
        # Subquery complexity
        subquery_count = sql.count("(SELECT")
        complexity += subquery_count * 15
        
        # DISTINCT complexity
        if "DISTINCT" in sql.upper():
            complexity += 5
        
        # HAVING clause (post-aggregation filtering is expensive)
        if "HAVING" in sql.upper():
            complexity += 8
        
        return min(complexity, 100.0)
    
    async def _estimate_result_size(
        self, 
        sql: str, 
        query_info: Dict[str, Any]
    ) -> int:
        """
        Estimate number of rows in result.
        
        Strategy:
        1. Run COUNT(*) version of query
        2. If GROUP BY, estimate cardinality
        3. Apply LIMIT if present
        """
        try:
            # Check if query has GROUP BY
            dimensions = query_info.get("dimensions", [])
            
            if not dimensions:
                # No GROUP BY, result is single row
                return 1
            
            # Estimate cardinality of dimensions
            # For now, use simple heuristic: COUNT(DISTINCT dim)
            model = query_info.get("model", "users")
            table = query_info.get("table", model)
            
            # Query dimension cardinality
            cardinality_queries = []
            for dim in dimensions:
                cardinality_sql = f"SELECT COUNT(DISTINCT {dim}) as cardinality FROM {table}"
                cardinality_queries.append(cardinality_sql)
            
            # Execute first dimension cardinality (approximation)
            if cardinality_queries:
                result = self.connection.sql(cardinality_queries[0]).to_pandas()
                cardinality = result.iloc[0]['cardinality']
                
                # Multiply cardinalities for multi-dimensional queries
                estimated = cardinality
                if len(dimensions) > 1:
                    # Conservative estimate: multiply by sqrt(n) for additional dimensions
                    estimated *= (len(dimensions) ** 0.5)
                
                return int(estimated)
            
            return 1000  # Conservative default
            
        except Exception as e:
            logger.warning(f"Could not estimate result size: {e}")
            return 10000  # Conservative default if estimation fails
    
    def _check_for_warnings(self, sql: str, query_info: Dict[str, Any]) -> list[str]:
        """
        Check for potential issues that aren't errors but should be warned about.
        """
        warnings = []
        
        # Check 1: No filters on large tables
        if "WHERE" not in sql.upper():
            model = query_info.get("model")
            if model in ["events", "sessions"]:  # Known large tables
                warnings.append(
                    f"No filters applied to '{model}' table. Query may be slow."
                )
        
        # Check 2: Many dimensions without LIMIT
        dimensions = len(query_info.get("dimensions", []))
        if dimensions > 3 and "LIMIT" not in sql.upper():
            warnings.append(
                f"Query has {dimensions} dimensions without LIMIT. Consider adding LIMIT for faster results."
            )
        
        # Check 3: Cartesian products (multiple JOINs without proper conditions)
        join_count = sql.upper().count("JOIN")
        if join_count > 2 and sql.upper().count("ON") < join_count:
            warnings.append(
                "Potential cartesian product detected. Ensure all JOINs have proper ON conditions."
            )
        
        return warnings


# Integration with existing query_model tool
async def execute_validated_query(
    semantic_manager,
    query_info: Dict[str, Any],
    validator: QueryValidator
) -> Dict[str, Any]:
    """
    Execute query with validation.
    
    Usage in server.py:
        validator = QueryValidator(semantic_manager.connection)
        result = await execute_validated_query(semantic_manager, query_info, validator)
    """
    
    # Build Ibis query
    ibis_expr = semantic_manager.build_ibis_query(query_info)
    
    # Validate before execution
    validation = await validator.validate_ibis_query(ibis_expr, query_info)
    
    if not validation.valid:
        return {
            "error": validation.error,
            "validation": validation,
            "data": [],
            "executed": False
        }
    
    # Validation passed, execute query
    result = await semantic_manager.execute_query(query_info)
    
    # Add validation metadata to result
    result["validation"] = {
        "complexity_score": validation.complexity_score,
        "estimated_rows": validation.estimated_rows,
        "warnings": validation.warnings
    }
    
    return result
```

**Integration Point**: Add to `mcp_server/server.py` in the `query_model` tool before execution.

**Testing Strategy**:
```python
# Test cases
test_cases = [
    {
        "name": "simple_query",
        "query_info": {
            "model": "users",
            "dimensions": ["plan_type"],
            "measures": ["total_users"]
        },
        "expected": {"valid": True}
    },
    {
        "name": "complex_query_blocked",
        "query_info": {
            "model": "events",
            "dimensions": ["user_id", "event_type", "date", "hour", "feature_name"],
            "measures": ["total_events", "unique_users", "avg_duration"]
        },
        "expected": {"valid": False, "reason": "too_complex"}
    },
    {
        "name": "no_limit_on_large_table",
        "query_info": {
            "model": "events",
            "dimensions": ["event_type"],
            "measures": ["total_events"]
        },
        "expected": {"valid": True, "warnings": ["No filters applied"]}
    }
]
```

**Estimated Effort**: 1 week (design, implement, test)

**Impact**: High - Prevents query failures and improves user experience

---

### 2. RAG Model Discovery

**Rationale**:
- With 10+ semantic models, finding the right one is hard
- Users shouldn't need to know model names
- Vector search enables natural language model selection
- **Gap in claude-analyst**: Users must know exact model names

**WrenAI Pattern**:
```python
# Embed model descriptions
embeddings = qdrant.search(user_question, top_k=3)
relevant_models = [emb.model_name for emb in embeddings]
```

**Claude-Analyst Implementation** (Clean-Room, No External Vector DB):

```python
# File: semantic-layer/mcp_server/model_discovery.py

import json
import logging
import numpy as np
from pathlib import Path
from typing import Any, Dict, List, Tuple
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class ModelDiscovery:
    """
    Discover relevant semantic models using vector similarity search.
    
    Uses lightweight SentenceTransformers (no external vector DB needed).
    Embeddings cached locally for fast lookup.
    """
    
    def __init__(self, models_path: Path):
        self.models_path = models_path
        
        # Use small, fast embedding model (33MB, CPU-friendly)
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Cache: {model_name: embedding_vector}
        self.model_embeddings: Dict[str, np.ndarray] = {}
        
        # Cache: {model_name: searchable_text}
        self.model_descriptions: Dict[str, str] = {}
        
        # Load and embed models
        self._load_and_embed_models()
    
    def _load_and_embed_models(self):
        """Load semantic models and create embeddings"""
        
        import yaml
        
        for model_file in self.models_path.glob("*.yml"):
            try:
                with open(model_file, "r") as f:
                    model_config = yaml.safe_load(f)
                
                model_name = model_config["model"]["name"]
                
                # Build searchable description
                description_parts = [
                    model_config["model"].get("description", ""),
                    f"Table: {model_config['model'].get('table', '')}",
                ]
                
                # Add dimension names and descriptions
                for dim in model_config.get("dimensions", []):
                    description_parts.append(f"Dimension: {dim['name']} - {dim.get('description', '')}")
                
                # Add measure names and descriptions
                for measure in model_config.get("measures", []):
                    description_parts.append(f"Measure: {measure['name']} - {measure.get('description', '')}")
                
                # Add context
                context = model_config.get("context", {})
                for key, value in context.items():
                    description_parts.append(f"{key}: {value}")
                
                # Combine into searchable text
                searchable_text = " ".join(filter(None, description_parts))
                
                # Create embedding
                embedding = self.embedder.encode(searchable_text, convert_to_numpy=True)
                
                # Cache
                self.model_embeddings[model_name] = embedding
                self.model_descriptions[model_name] = searchable_text
                
                logger.info(f"Embedded model: {model_name}")
                
            except Exception as e:
                logger.error(f"Failed to embed model {model_file}: {e}")
    
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
            top_k: Number of models to return
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of models with similarity scores
        """
        
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
                "description": self.model_descriptions[model_name][:200]  # Truncate
            })
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Filter by threshold and limit to top_k
        results = [
            s for s in similarities 
            if s["similarity"] >= similarity_threshold
        ][:top_k]
        
        return results
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        return dot_product / (norm1 * norm2)
    
    async def suggest_dimensions_and_measures(
        self,
        user_question: str,
        model_name: str
    ) -> Dict[str, List[str]]:
        """
        Suggest relevant dimensions and measures for a model based on question.
        
        Example:
            Q: "What's revenue by industry?"
            Model: "users"
            Returns: {
                "dimensions": ["industry"],
                "measures": ["total_revenue"]
            }
        """
        
        # This is a placeholder for future enhancement
        # Could use entity extraction or embedding similarity on dimensions/measures
        
        return {
            "dimensions": [],
            "measures": [],
            "confidence": 0.0
        }


# MCP Tool Integration
@mcp.tool()
async def discover_models_for_question(question: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Discover relevant semantic models for a natural language question.
    
    Args:
        question: User's question in natural language
        top_k: Number of models to suggest (default: 3)
        
    Returns:
        Ranked list of relevant models with similarity scores
        
    Example:
        Q: "What's our monthly revenue growth?"
        Returns: [
            {"model": "revenue", "similarity": 0.87, "description": "..."},
            {"model": "users", "similarity": 0.65, "description": "..."},
        ]
    """
    try:
        # Initialize model discovery (could be cached globally)
        models_path = Path(__file__).parent.parent / "models"
        discovery = ModelDiscovery(models_path)
        
        # Discover relevant models
        results = await discovery.discover_models(question, top_k=top_k)
        
        return {
            "question": question,
            "relevant_models": results,
            "top_model": results[0]["model"] if results else None,
            "status": "success"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to discover models",
            "status": "error"
        }
```

**Dependencies**:
```bash
# Add to requirements.txt
sentence-transformers==2.2.2  # 33MB model, fast on CPU
```

**Integration Point**: 
1. Add `discover_models_for_question` MCP tool to `server.py`
2. Enhance `query_model` tool to auto-discover model if not provided

**Testing Strategy**:
```python
test_questions = [
    {
        "question": "What's our revenue this month?",
        "expected_top_model": "revenue",
        "expected_similarity": 0.7
    },
    {
        "question": "How many users signed up last week?",
        "expected_top_model": "users",
        "expected_similarity": 0.7
    },
    {
        "question": "What features do users use most?",
        "expected_top_model": "events",
        "expected_similarity": 0.6
    }
]
```

**Estimated Effort**: 1 week (embed models, implement search, test accuracy)

**Impact**: High - Dramatically improves user experience

---

### 3. Runtime Metric Definitions

**Rationale**:
- Users want to define custom metrics without editing YAML files
- Ad-hoc analysis requires flexible metric creation
- **Gap in claude-analyst**: All metrics must be pre-defined in YAML

**WrenAI Pattern**:
```json
// Define metric via API
{
  "name": "power_users",
  "type": "count_distinct",
  "dimension": "user_id",
  "filters": {"login_count": {">": 100}}
}
```

**Claude-Analyst Implementation** (Clean-Room):

```python
# File: semantic-layer/mcp_server/runtime_metrics.py

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class RuntimeMetric:
    """User-defined runtime metric"""
    name: str
    type: str  # count, count_distinct, sum, avg, ratio, custom_sql
    model: str
    description: str = ""
    
    # For standard aggregations
    dimension: Optional[str] = None
    
    # For ratio metrics
    numerator: Optional[str] = None
    denominator: Optional[str] = None
    
    # For custom SQL
    sql: Optional[str] = None
    
    # Filters
    filters: Dict[str, Any] = None
    
    # Metadata
    created_by: str = "user"
    created_at: str = ""
    tags: List[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if self.filters is None:
            self.filters = {}
        if self.tags is None:
            self.tags = []


class RuntimeMetricRegistry:
    """
    Manages user-defined runtime metrics.
    
    Features:
    - Define metrics at runtime
    - Persist to JSON file
    - Validate against semantic models
    - Integration with query execution
    """
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.metrics: Dict[str, RuntimeMetric] = {}
        
        # Load existing metrics
        self._load_metrics()
    
    def _load_metrics(self):
        """Load runtime metrics from storage"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                
                for metric_data in data.get("metrics", []):
                    metric = RuntimeMetric(**metric_data)
                    self.metrics[metric.name] = metric
                
                logger.info(f"Loaded {len(self.metrics)} runtime metrics")
                
            except Exception as e:
                logger.error(f"Failed to load runtime metrics: {e}")
    
    def _save_metrics(self):
        """Persist runtime metrics to storage"""
        try:
            data = {
                "metrics": [asdict(m) for m in self.metrics.values()],
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved {len(self.metrics)} runtime metrics")
            
        except Exception as e:
            logger.error(f"Failed to save runtime metrics: {e}")
    
    async def define_metric(
        self,
        name: str,
        type: str,
        model: str,
        semantic_manager,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Define a new runtime metric.
        
        Args:
            name: Metric name (unique identifier)
            type: Metric type (count, count_distinct, sum, avg, ratio, custom_sql)
            model: Semantic model this metric belongs to
            semantic_manager: For validation
            **kwargs: Additional metric parameters
            
        Returns:
            Status and created metric details
        """
        
        # Validate metric name
        if name in self.metrics:
            return {
                "error": f"Metric '{name}' already exists",
                "status": "error"
            }
        
        # Validate model exists
        available_models = await semantic_manager.get_available_models()
        model_names = [m["name"] for m in available_models]
        
        if model not in model_names:
            return {
                "error": f"Model '{model}' not found. Available: {model_names}",
                "status": "error"
            }
        
        # Validate metric type
        valid_types = ["count", "count_distinct", "sum", "avg", "ratio", "custom_sql"]
        if type not in valid_types:
            return {
                "error": f"Invalid metric type '{type}'. Valid: {valid_types}",
                "status": "error"
            }
        
        # Create metric
        metric = RuntimeMetric(
            name=name,
            type=type,
            model=model,
            **kwargs
        )
        
        # Validate metric can be executed
        validation_result = await self._validate_metric(metric, semantic_manager)
        
        if not validation_result["valid"]:
            return {
                "error": f"Metric validation failed: {validation_result['error']}",
                "status": "error"
            }
        
        # Store metric
        self.metrics[name] = metric
        self._save_metrics()
        
        return {
            "metric": asdict(metric),
            "status": "success",
            "message": f"Metric '{name}' created successfully"
        }
    
    async def _validate_metric(
        self,
        metric: RuntimeMetric,
        semantic_manager
    ) -> Dict[str, Any]:
        """
        Validate metric can be executed.
        
        Checks:
        - Dimension exists in model
        - SQL is valid (for custom_sql)
        - Ratio numerator/denominator are valid
        """
        try:
            # Get model schema
            model_schema = await semantic_manager.get_model_schema(metric.model)
            
            # Validate dimension exists
            if metric.dimension:
                available_dims = [d["name"] for d in model_schema["dimensions"]]
                if metric.dimension not in available_dims:
                    return {
                        "valid": False,
                        "error": f"Dimension '{metric.dimension}' not found in model '{metric.model}'"
                    }
            
            # Validate ratio components
            if metric.type == "ratio":
                if not metric.numerator or not metric.denominator:
                    return {
                        "valid": False,
                        "error": "Ratio metrics require 'numerator' and 'denominator'"
                    }
            
            # Validate custom SQL (basic check)
            if metric.type == "custom_sql":
                if not metric.sql:
                    return {
                        "valid": False,
                        "error": "Custom SQL metrics require 'sql' parameter"
                    }
                
                # Could add SQL parsing here for deeper validation
            
            return {"valid": True}
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }
    
    def get_metric(self, name: str) -> Optional[RuntimeMetric]:
        """Get runtime metric by name"""
        return self.metrics.get(name)
    
    def list_metrics(
        self,
        model: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[RuntimeMetric]:
        """
        List runtime metrics with optional filtering.
        
        Args:
            model: Filter by model name
            tags: Filter by tags (any match)
            
        Returns:
            List of matching metrics
        """
        metrics = list(self.metrics.values())
        
        if model:
            metrics = [m for m in metrics if m.model == model]
        
        if tags:
            metrics = [m for m in metrics if any(tag in m.tags for tag in tags)]
        
        return metrics
    
    async def delete_metric(self, name: str) -> Dict[str, Any]:
        """Delete a runtime metric"""
        if name not in self.metrics:
            return {
                "error": f"Metric '{name}' not found",
                "status": "error"
            }
        
        del self.metrics[name]
        self._save_metrics()
        
        return {
            "message": f"Metric '{name}' deleted successfully",
            "status": "success"
        }


# MCP Tool Integration
@mcp.tool()
async def define_custom_metric(
    name: str,
    type: str,
    model: str,
    description: str = "",
    dimension: Optional[str] = None,
    numerator: Optional[str] = None,
    denominator: Optional[str] = None,
    sql: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Define a custom metric at runtime.
    
    Args:
        name: Unique metric name
        type: Metric type (count, count_distinct, sum, avg, ratio, custom_sql)
        model: Semantic model this metric belongs to
        description: Human-readable description
        dimension: Column to aggregate (for count_distinct, sum, avg)
        numerator: Numerator metric (for ratio)
        denominator: Denominator metric (for ratio)
        sql: Custom SQL expression (for custom_sql)
        filters: Optional filters to apply
        tags: Tags for organization
        
    Returns:
        Created metric details
        
    Example:
        define_custom_metric(
            name="power_users",
            type="count_distinct",
            model="users",
            dimension="user_id",
            filters={"login_count": {">": 100}},
            description="Users with 100+ logins",
            tags=["engagement", "power_users"]
        )
    """
    try:
        # Initialize registry (could be cached globally)
        storage_path = Path(__file__).parent.parent / "data" / "runtime_metrics.json"
        registry = RuntimeMetricRegistry(storage_path)
        
        # Define metric
        result = await registry.define_metric(
            name=name,
            type=type,
            model=model,
            semantic_manager=semantic_manager,
            description=description,
            dimension=dimension,
            numerator=numerator,
            denominator=denominator,
            sql=sql,
            filters=filters or {},
            tags=tags or []
        )
        
        return result
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to define custom metric",
            "status": "error"
        }


@mcp.tool()
async def list_custom_metrics(
    model: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    List all custom metrics with optional filtering.
    
    Args:
        model: Filter by model name
        tags: Filter by tags
        
    Returns:
        List of custom metrics
    """
    try:
        storage_path = Path(__file__).parent.parent / "data" / "runtime_metrics.json"
        registry = RuntimeMetricRegistry(storage_path)
        
        metrics = registry.list_metrics(model=model, tags=tags)
        
        return {
            "metrics": [asdict(m) for m in metrics],
            "total_count": len(metrics),
            "status": "success"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to list custom metrics",
            "status": "error"
        }


@mcp.tool()
async def delete_custom_metric(name: str) -> Dict[str, Any]:
    """Delete a custom metric by name"""
    try:
        storage_path = Path(__file__).parent.parent / "data" / "runtime_metrics.json"
        registry = RuntimeMetricRegistry(storage_path)
        
        return await registry.delete_metric(name)
        
    except Exception as e:
        return {
            "error": str(e),
            "message": f"Failed to delete metric '{name}'",
            "status": "error"
        }
```

**Integration Point**: 
1. Add 3 MCP tools: `define_custom_metric`, `list_custom_metrics`, `delete_custom_metric`
2. Enhance `SemanticLayerManager.build_query()` to support runtime metrics

**Testing Strategy**:
```python
test_cases = [
    {
        "metric": {
            "name": "power_users",
            "type": "count_distinct",
            "model": "users",
            "dimension": "user_id",
            "filters": {"login_count__gt": 100}
        },
        "expected_query": "COUNT(DISTINCT user_id) WHERE login_count > 100"
    },
    {
        "metric": {
            "name": "conversion_rate",
            "type": "ratio",
            "model": "users",
            "numerator": "paid_users",
            "denominator": "total_users"
        },
        "expected_query": "COUNT(CASE WHEN plan_type != 'free'...) / COUNT(*)"
    }
]
```

**Estimated Effort**: 1 week (design, implement, test, integrate)

**Impact**: High - Enables ad-hoc metric creation without code changes

---

## Priority 2: Medium-Impact Components

### 4. Visualization Layer

**Rationale**:
- Charts communicate insights better than tables
- **Gap in claude-analyst**: No visualization capability

**Implementation**: See full code in appendix.

**Estimated Effort**: 1 week

**Impact**: Medium - Nice-to-have, not critical

### 5. Multi-Database Support

**Rationale**:
- Production data often in Postgres/BigQuery, not DuckDB
- Cross-database analysis is powerful

**Implementation**: Database connector abstraction (see appendix).

**Estimated Effort**: 2 weeks (per database type)

**Impact**: Medium - Expands use cases significantly

---

## Appendix A: Visualization Layer (Abbreviated)

```python
# File: semantic-layer/mcp_server/visualization.py

class ChartGenerator:
    """Generate charts from query results"""
    
    async def infer_chart_type(self, data: pd.DataFrame) -> str:
        """Infer best chart type from data structure"""
        # Time series → Line chart
        # Categories → Bar chart
        # Correlation → Scatter plot
        pass
    
    async def generate_plotly_chart(self, data: pd.DataFrame, chart_type: str):
        """Generate Plotly chart code"""
        pass
```

**MCP Tool**: `visualize_results(data, chart_type="auto")`

---

## Appendix B: Multi-Database Support (Abbreviated)

```python
# File: semantic-layer/mcp_server/database_connectors.py

class DatabaseConnector:
    """Abstract database connector"""
    
    async def connect(self, config: Dict[str, Any]):
        pass
    
    async def execute(self, query):
        pass


class PostgresConnector(DatabaseConnector):
    """PostgreSQL connector using psycopg2 + Ibis"""
    pass


class BigQueryConnector(DatabaseConnector):
    """BigQuery connector using google-cloud-bigquery + Ibis"""
    pass
```

**MCP Tools**: `connect_database(type, config)`, `list_databases()`, `query_database(db_name, query)`

---

## Implementation Timeline

### Week 1: SQL Validation
- Design validator interface
- Implement dry-run validation
- Add complexity analysis
- Test with edge cases

### Week 2: RAG Model Discovery
- Integrate SentenceTransformers
- Embed semantic models
- Implement vector search
- Test discovery accuracy

### Week 3: Runtime Metrics
- Design metric registry
- Implement CRUD operations
- Add query integration
- Test metric execution

### Week 4: Visualization (Optional)
- Implement chart type inference
- Build Plotly code generator
- Create MCP tool
- Test with various datasets

### Week 5-6: Multi-Database (Optional)
- Design connector interface
- Implement Postgres connector
- Implement BigQuery connector
- Test cross-database queries

---

## Success Metrics

| Component | Metric | Target |
|-----------|--------|--------|
| SQL Validation | Error prevention rate | >90% |
| RAG Discovery | Model selection accuracy | >85% |
| Runtime Metrics | User adoption | 10+ custom metrics in first month |
| Visualization | Chart quality | User satisfaction >4/5 |
| Multi-Database | Supported databases | 3+ (DuckDB, Postgres, BigQuery) |

---

## Conclusion

These components, implemented clean-room style, will significantly enhance claude-analyst while maintaining our unique differentiators (statistical rigor, optimization, conversation memory, workflows).

**Key Recommendations**:
1. ✅ Implement P1 components first (SQL validation, RAG, runtime metrics)
2. ✅ Use lightweight dependencies (SentenceTransformers, not Qdrant)
3. ✅ Maintain AGPL-3.0 compliance through independent implementation
4. ✅ Extensive testing before production deployment

**Next Steps**: Begin Phase 5.1 (SQL Validation Layer) immediately.

---

**Document Status**: ✅ Complete  
**Last Updated**: 2025-11-11
