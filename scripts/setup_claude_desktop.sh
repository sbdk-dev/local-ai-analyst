#!/bin/bash
# Auto-configure Claude Desktop for AI Analyst MCP Server
# This script creates/updates the Claude Desktop config with correct paths

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  AI Analyst - Claude Desktop Setup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Detect script directory and semantic-layer path
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SEMANTIC_LAYER_DIR="$(dirname "$SCRIPT_DIR")/semantic-layer"

# Find uv path
UV_PATH=$(which uv 2>/dev/null || echo "uv")
if [ "$UV_PATH" = "uv" ]; then
    echo -e "${YELLOW}⚠ Warning: 'uv' not found in PATH${NC}"
    echo -e "${YELLOW}Will use 'uv' but you may need to update config manually${NC}"
    echo ""
fi

# Detect platform
if [[ "$OSTYPE" == "darwin"* ]]; then
    CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
    PLATFORM="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CLAUDE_CONFIG_DIR="$HOME/.config/Claude"
    PLATFORM="Linux"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    CLAUDE_CONFIG_DIR="$APPDATA/Claude"
    PLATFORM="Windows"
else
    echo -e "${RED}✗ Unknown operating system: $OSTYPE${NC}"
    echo -e "${YELLOW}Please manually configure Claude Desktop${NC}"
    exit 1
fi

CLAUDE_CONFIG="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

echo -e "${BLUE}Platform:${NC} $PLATFORM"
echo -e "${BLUE}Config location:${NC} $CLAUDE_CONFIG"
echo -e "${BLUE}Semantic layer:${NC} $SEMANTIC_LAYER_DIR"
echo ""

# Verify semantic-layer directory exists
if [ ! -d "$SEMANTIC_LAYER_DIR" ]; then
    echo -e "${RED}✗ Error: Semantic layer directory not found${NC}"
    echo -e "${YELLOW}Expected: $SEMANTIC_LAYER_DIR${NC}"
    echo ""
    echo "Please run this script from the claude-analyst repository root:"
    echo "  ./scripts/setup_claude_desktop.sh"
    exit 1
fi

# Verify run_mcp_server.py exists
if [ ! -f "$SEMANTIC_LAYER_DIR/run_mcp_server.py" ]; then
    echo -e "${RED}✗ Error: run_mcp_server.py not found${NC}"
    echo -e "${YELLOW}Expected: $SEMANTIC_LAYER_DIR/run_mcp_server.py${NC}"
    exit 1
fi

# Create config directory if it doesn't exist
mkdir -p "$CLAUDE_CONFIG_DIR"

# Backup existing config if it exists
if [ -f "$CLAUDE_CONFIG" ]; then
    BACKUP_FILE="$CLAUDE_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${YELLOW}⚠ Existing config found - creating backup${NC}"
    cp "$CLAUDE_CONFIG" "$BACKUP_FILE"
    echo -e "${GREEN}✓ Backup created: $BACKUP_FILE${NC}"
    echo ""

    # Check if config already has ai-analyst
    if grep -q "ai-analyst" "$CLAUDE_CONFIG"; then
        echo -e "${YELLOW}⚠ 'ai-analyst' already exists in config${NC}"
        echo ""
        read -p "Do you want to update it? (y/n) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}ℹ Setup cancelled - existing config unchanged${NC}"
            exit 0
        fi

        # Update existing config
        # This is complex with jq, so we'll just show manual instructions
        echo -e "${YELLOW}⚠ Automatic update of existing config not supported${NC}"
        echo ""
        echo "Please manually update the 'ai-analyst' entry in:"
        echo "  $CLAUDE_CONFIG"
        echo ""
        echo "Set 'cwd' to:"
        echo "  $SEMANTIC_LAYER_DIR"
        echo ""
        exit 0
    fi
fi

# Generate new config or append to existing
if [ -f "$CLAUDE_CONFIG" ]; then
    # Config exists but doesn't have ai-analyst - need to merge
    echo -e "${YELLOW}⚠ Merging with existing config requires jq${NC}"

    # Check if jq is available
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}✗ jq not found - please install it:${NC}"
        echo "  macOS: brew install jq"
        echo "  Linux: apt-get install jq or yum install jq"
        echo ""
        echo "Or manually add this to your config:"
        echo ""
        cat <<EOF
{
  "mcpServers": {
    "ai-analyst": {
      "command": "$UV_PATH",
      "args": ["run", "python", "run_mcp_server.py"],
      "cwd": "$SEMANTIC_LAYER_DIR"
    }
  }
}
EOF
        echo ""
        exit 1
    fi

    # Merge configs
    echo -e "${BLUE}ℹ Merging with existing configuration...${NC}"
    jq --arg cwd "$SEMANTIC_LAYER_DIR" --arg uv_path "$UV_PATH" '.mcpServers["ai-analyst"] = {
      "command": $uv_path,
      "args": ["run", "python", "run_mcp_server.py"],
      "cwd": $cwd
    }' "$CLAUDE_CONFIG" > "$CLAUDE_CONFIG.tmp"
    mv "$CLAUDE_CONFIG.tmp" "$CLAUDE_CONFIG"
else
    # Create new config
    echo -e "${BLUE}ℹ Creating new configuration...${NC}"
    cat > "$CLAUDE_CONFIG" <<EOF
{
  "mcpServers": {
    "ai-analyst": {
      "command": "$UV_PATH",
      "args": ["run", "python", "run_mcp_server.py"],
      "cwd": "$SEMANTIC_LAYER_DIR"
    }
  }
}
EOF
fi

echo ""
echo -e "${GREEN}✓ Claude Desktop configured successfully!${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo "  1. ${YELLOW}Quit Claude Desktop completely${NC} (Cmd+Q on Mac)"
echo "  2. ${YELLOW}Reopen Claude Desktop${NC}"
echo "  3. ${YELLOW}Wait 5-10 seconds${NC} for MCP server to initialize"
echo "  4. ${YELLOW}Try your first query:${NC}"
echo ""
echo "     \"List available data models\""
echo ""
echo -e "${BLUE}Configuration saved to:${NC}"
echo "  $CLAUDE_CONFIG"
echo ""
echo -e "${BLUE}To verify setup works:${NC}"
echo "  cd $SEMANTIC_LAYER_DIR"
echo "  uv run python -c \"from mcp_server.semantic_layer_integration import SemanticLayerManager; import asyncio; asyncio.run(SemanticLayerManager().initialize())\""
echo ""
echo -e "${GREEN}Happy analyzing! 📊${NC}"
echo ""
