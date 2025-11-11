#!/usr/bin/env python3
"""Manual test to see the actual output of list_available_models()"""

import asyncio
import json
from mcp_server.semantic_layer_integration import SemanticLayerManager


async def main():
    # Initialize manager
    manager = SemanticLayerManager()
    await manager.initialize()

    # Call the new method
    models = await manager.list_available_models()

    # Pretty print the results
    print("=" * 80)
    print("list_available_models() Output:")
    print("=" * 80)
    print(json.dumps(models, indent=2))
    print()
    print(f"Total models: {len(models)}")


if __name__ == "__main__":
    asyncio.run(main())
