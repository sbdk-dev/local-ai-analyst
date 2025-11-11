#!/usr/bin/env python3
import asyncio
from mcp_server.semantic_layer_integration import SemanticLayerManager

async def main():
    m = SemanticLayerManager()
    await m._load_models()

    q = await m.build_query('users', ['plan_type'], ['total_users'], {})
    print('Query:', q)

    r = await m.execute_query(q)
    print('Result keys:', r.keys())
    print('Data type:', type(r.get('data')))
    print('Data length:', len(r.get('data', [])) if r.get('data') else 0)
    print('Data sample:', r.get('data', [])[:2] if r.get('data') else [])
    print('Full result:', r)

asyncio.run(main())
