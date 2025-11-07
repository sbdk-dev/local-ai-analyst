#!/usr/bin/env python3
"""
Entry point script for AI Analyst MCP Server
This ensures the module path is set up correctly for Claude Desktop
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path so mcp_server module can be found
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import and run the server
from mcp_server.server import main

if __name__ == "__main__":
    main()