"""
AI Analyst MCP Server

FastMCP server implementation for semantic layer integration with Claude Desktop.
Implements execution-first pattern to prevent fabrication with statistical rigor.
"""

from .intelligence_layer import IntelligenceEngine
from .semantic_layer_integration import SemanticLayerManager
from .server import main, mcp
from .statistical_testing import StatisticalTester

__all__ = [
    "mcp",
    "main",
    "SemanticLayerManager",
    "IntelligenceEngine",
    "StatisticalTester",
]

__version__ = "1.0.0"
