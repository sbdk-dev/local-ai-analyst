"""
Basic Query Example

This example shows how to query the semantic layer programmatically.
"""

import asyncio
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "semantic-layer"))

from mcp_server.semantic_layer_integration import SemanticLayerManager


async def main():
    """Run basic query examples"""
    print("=" * 60)
    print("Claude-Analyst - Basic Query Example")
    print("=" * 60)
    print()

    # Initialize the semantic layer manager
    manager = SemanticLayerManager()
    await manager.initialize()

    # Example 1: Get total user count
    print("📊 Example 1: Total User Count")
    print("-" * 60)
    result1 = await manager.build_and_execute_query(
        model_name="users",
        dimensions=[],
        measures=["total_users"],
    )
    print(f"Total Users: {result1['data'][0]['total_users']:,}")
    print()

    # Example 2: Users by plan type
    print("📊 Example 2: Users by Plan Type")
    print("-" * 60)
    result2 = await manager.build_and_execute_query(
        model_name="users",
        dimensions=["plan_type"],
        measures=["total_users"],
    )
    for row in result2["data"]:
        print(f"{row['plan_type']}: {row['total_users']:,} users")
    print()

    # Example 3: Conversion rate by industry
    print("📊 Example 3: Conversion Rate by Industry")
    print("-" * 60)
    result3 = await manager.build_and_execute_query(
        model_name="users",
        dimensions=["industry"],
        measures=["conversion_rate"],
        limit=5,
    )
    for row in result3["data"]:
        print(f"{row['industry']}: {row['conversion_rate']:.1%}")
    print()

    print("✅ All examples completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
