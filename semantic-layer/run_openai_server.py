#!/usr/bin/env python3
"""
OpenAI API Server for ChatGPT Desktop Integration

This server exposes the Claude-Analyst functionality through OpenAI's function calling API,
allowing ChatGPT Desktop to interact with the semantic layer.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from mcp_server.semantic_layer_integration import SemanticLayerManager
from mcp_server.intelligence_layer import IntelligenceEngine
from mcp_server.statistical_testing import StatisticalTester
from mcp_server.conversation_memory import ConversationMemory
from mcp_server.query_optimizer import QueryOptimizer
from mcp_server.workflow_orchestrator import WorkflowOrchestrator
from mcp_server.query_validator import QueryValidator
from mcp_server.model_discovery import ModelDiscovery
from mcp_server.runtime_metrics import get_registry
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Claude-Analyst OpenAI API",
    description="AI Data Analyst with semantic layer integration",
    version="1.0.0",
)

# Add CORS middleware for ChatGPT Desktop
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
semantic_manager = SemanticLayerManager()
intelligence_engine = IntelligenceEngine()
statistical_tester = StatisticalTester()
conversation_memory = ConversationMemory()
query_optimizer = QueryOptimizer()
workflow_orchestrator = WorkflowOrchestrator()
query_validator = QueryValidator()

models_path = Path(__file__).parent / "models"
model_discovery = ModelDiscovery(models_path, lazy_load=True)

runtime_metrics_storage = Path(__file__).parent / "data" / "runtime_metrics.json"
runtime_metrics_registry = get_registry(runtime_metrics_storage)


# Pydantic models for OpenAI API
class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str = "gpt-4"
    messages: List[Message]
    functions: List[Dict] = []
    function_call: str = "auto"


class ChatResponse(BaseModel):
    id: str = "chatcmpl-analyst"
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict]


# Function definitions for ChatGPT
FUNCTIONS = [
    {
        "name": "list_available_models",
        "description": "List all available semantic data models",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "query_model",
        "description": "Query a semantic model with dimensions and measures",
        "parameters": {
            "type": "object",
            "properties": {
                "model_name": {
                    "type": "string",
                    "description": "Name of the semantic model to query",
                },
                "dimensions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Dimensions to group by",
                },
                "measures": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Measures to calculate",
                },
                "filters": {
                    "type": "object",
                    "description": "Filters to apply",
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of rows to return",
                },
            },
            "required": ["model_name"],
        },
    },
    {
        "name": "discover_models_for_question",
        "description": "Find relevant data models for a natural language question",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Natural language question about data",
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of models to return",
                    "default": 3,
                },
            },
            "required": ["question"],
        },
    },
    {
        "name": "run_workflow",
        "description": "Run a pre-built analytical workflow",
        "parameters": {
            "type": "object",
            "properties": {
                "workflow_name": {
                    "type": "string",
                    "description": "Name of the workflow (conversion_analysis, feature_usage_analysis, revenue_optimization)",
                },
                "params": {
                    "type": "object",
                    "description": "Parameters for the workflow",
                },
            },
            "required": ["workflow_name"],
        },
    },
]


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Claude-Analyst OpenAI API",
        "version": "1.0.0",
        "models_loaded": len(await semantic_manager.get_available_models()),
    }


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    """OpenAI plugin manifest for ChatGPT"""
    return {
        "schema_version": "v1",
        "name_for_human": "Claude-Analyst",
        "name_for_model": "claude_analyst",
        "description_for_human": "AI data analyst with semantic layer and statistical rigor",
        "description_for_model": "Query and analyze data using semantic models. Supports natural language queries, statistical testing, and pre-built workflows.",
        "auth": {"type": "none"},
        "api": {"type": "openapi", "url": "http://localhost:8000/openapi.json"},
        "logo_url": "http://localhost:8000/logo.png",
        "contact_email": "support@example.com",
        "legal_info_url": "http://localhost:8000/legal",
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    """
    OpenAI-compatible chat completions endpoint

    This endpoint handles function calling for ChatGPT Desktop
    """
    try:
        # Get the last user message
        user_message = next(
            (msg.content for msg in reversed(request.messages) if msg.role == "user"),
            "",
        )

        logger.info(f"Received chat request: {user_message}")

        # Simple routing logic - in production, use an LLM to parse intent
        response_content = await route_request(user_message)

        return {
            "id": "chatcmpl-analyst",
            "object": "chat.completion",
            "created": int(asyncio.get_event_loop().time()),
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": response_content},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def route_request(user_message: str) -> str:
    """
    Route user message to appropriate function

    In production, use an LLM to parse intent and extract parameters
    """
    message_lower = user_message.lower()

    # List models
    if any(keyword in message_lower for keyword in ["list", "show", "available models"]):
        models = await semantic_manager.get_available_models()
        model_list = "\n".join([f"- **{m['name']}**: {m['description']}" for m in models])
        return f"📊 Available Data Models:\n\n{model_list}"

    # Query model (simplified - in production, parse dimensions/measures from NL)
    elif "user" in message_lower and ("count" in message_lower or "how many" in message_lower):
        result = await semantic_manager.build_and_execute_query(
            model_name="users",
            dimensions=[],
            measures=["total_users"],
        )
        total = result["data"][0]["total_users"] if result["data"] else 0
        return f"👥 Total Users: **{total:,}**"

    # Default response
    else:
        return f"""I can help you analyze data! Try asking:

- "List available data models"
- "How many users do we have?"
- "Show me conversion rate by plan type"
- "Run a comprehensive conversion analysis"

Available functions:
{chr(10).join([f"- {f['name']}: {f['description']}" for f in FUNCTIONS])}
"""


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    logger.info("Starting Claude-Analyst OpenAI API Server...")

    await semantic_manager.initialize()
    models = await semantic_manager.get_available_models()

    logger.info(f"✅ Loaded {len(models)} semantic models")
    logger.info("✅ Server ready at http://localhost:8000")
    logger.info("📖 API docs at http://localhost:8000/docs")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Claude-Analyst OpenAI API Server")
    print("="*60)
    print("\n📍 Server URL: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    print("🔌 For ChatGPT Desktop: Configure custom action to http://localhost:8000")
    print("\n" + "="*60 + "\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
