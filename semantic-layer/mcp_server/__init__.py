"""
AI Analyst MCP Server

FastMCP server implementation for semantic layer integration with Claude Desktop.
Implements execution-first pattern to prevent fabrication with statistical rigor.
"""

from .server import mcp, main
from .semantic_layer_integration import SemanticLayerManager
from .intelligence_layer import IntelligenceEngine
from .statistical_testing import StatisticalTester

__all__ = [
    'mcp',
    'main',
    'SemanticLayerManager',
    'IntelligenceEngine',
    'StatisticalTester'
]

__version__ = '1.0.0'