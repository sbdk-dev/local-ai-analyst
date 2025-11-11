# Quick Start - AI Analyst in 5 Minutes

Get the AI Analyst running and ask your first question in under 5 minutes.

---

## Prerequisites

Before starting, make sure you have:

- **Claude Desktop** installed → [Download here](https://claude.ai/download)
- **Python 3.11 or higher** installed
  ```bash
  # Check your version
  python3 --version
  # Should show: Python 3.11.x or higher
  ```
- **5 minutes** of your time

---

## Step 1: Install UV Package Manager

UV is a fast Python package manager. Install it with one command:

### macOS / Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Verify installation**:
```bash
uv --version
# Should show: uv x.x.x
```

---

## Step 2: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/claude-analyst.git
cd claude-analyst/semantic-layer

# Install dependencies (this creates a virtual environment and installs everything)
uv sync

# Verify installation
uv run python -c "print('✅ Installation successful!')"
```

**Expected output**: `✅ Installation successful!`

---

## Step 3: Configure Claude Desktop

### Automatic Setup (macOS only)

```bash
# Run the setup script (creates config with absolute path)
./scripts/setup_claude_desktop.sh
```

**Expected output**:
```
✅ Claude Desktop configured!
📍 Config location: ~/Library/Application Support/Claude/claude_desktop_config.json
🔄 Restart Claude Desktop to activate
```

### Manual Setup (All Platforms)

1. **Find your config file location**:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Get your full path** to the semantic-layer directory:
   ```bash
   pwd
   # Copy this output - you'll need it in the next step
   ```

3. **Find the full path to uv**:
   ```bash
   which uv
   # Common locations:
   # macOS (Homebrew): /opt/homebrew/bin/uv
   # macOS (curl install): ~/.cargo/bin/uv
   # Linux: ~/.cargo/bin/uv
   # Windows: %USERPROFILE%\.cargo\bin\uv.exe
   ```

4. **Edit the config file** and add this (replace paths with your actual paths):

   ```json
   {
     "mcpServers": {
       "ai-analyst": {
         "command": "/opt/homebrew/bin/uv",
         "args": ["run", "python", "run_mcp_server.py"],
         "cwd": "/FULL/PATH/TO/claude-analyst/semantic-layer"
       }
     }
   }
   ```

   **Example** (what it should look like):
   ```json
   {
     "mcpServers": {
       "ai-analyst": {
         "command": "/opt/homebrew/bin/uv",
         "args": ["run", "python", "run_mcp_server.py"],
         "cwd": "/Users/yourname/Documents/claude-analyst/semantic-layer"
       }
     }
   }
   ```

   **Important**:
   - Use the **full path** to `uv` (from `which uv`)
   - Use the **full path** to your semantic-layer directory (from `pwd`)
   - GUI apps don't inherit your shell's PATH, so `"command": "uv"` won't work

5. **Save the file** (make sure it's valid JSON - no trailing commas!)

---

## Step 4: Verify Setup

Before restarting Claude Desktop, verify everything works locally:

```bash
cd semantic-layer

# Test 1: Check database exists
ls -la data/analytics.duckdb
# Should show: analytics.duckdb file exists

# Test 2: Verify semantic models load
uv run python -c "
from mcp_server.semantic_layer_integration import SemanticLayerManager
import asyncio
async def test():
    manager = SemanticLayerManager()
    await manager.initialize()
    models = await manager.get_available_models()
    print(f'✅ SUCCESS: {len(models)} models loaded')
    print(f'📊 Available: {[m[\"name\"] for m in models]}')
asyncio.run(test())
"
```

**Expected output**:
```
✅ SUCCESS: 3 models loaded
📊 Available: ['users', 'events', 'engagement']
```

**If you see this**, you're ready! If not, see [Troubleshooting](#troubleshooting) below.

---

## Step 5: Start Using It

### 5a. Restart Claude Desktop

1. **Quit Claude Desktop completely** (Cmd+Q on Mac, or close from system tray)
2. **Open Claude Desktop again**
3. **Wait 5 seconds** for the MCP server to initialize

### 5b. Verify Connection

In Claude Desktop, you should see a small indicator that MCP servers are connected (usually a tools icon or notification).

### 5c. Try Your First Query

Ask Claude:
```
List available data models
```

**Expected response**: Claude will list the 3 semantic models (users, events, engagement).

---

## Your First Queries

Now try these queries to explore the system:

### Beginner Queries
```
How many users do we have?
What's our conversion rate from free to paid?
Show me our user breakdown by plan type
```

### Intermediate Queries
```
Compare engagement between Pro and Free users
What are the top 5 features by usage?
Show me DAU trend for the last 30 days
```

### Advanced Queries
```
Is the difference in conversion rate statistically significant?
Run a comprehensive conversion analysis
Analyze feature adoption patterns across user segments
```

---

## What You Can Do

The AI Analyst provides:

### 23 MCP Tools
- **list_models** - See available data models
- **get_model** - Get detailed schema for a model
- **query_model** - Run queries with statistical analysis
- **suggest_analysis** - Get recommendations for next steps
- **test_significance** - Statistical testing on demand
- ...and 18 more advanced tools

### 3 Built-in Workflows
- **Conversion Analysis** - Full funnel analysis with cohort comparison
- **Feature Usage Analysis** - Adoption rates and engagement patterns
- **Revenue Optimization** - LTV, churn prediction, growth opportunities

### Conversation Memory
The system remembers your questions and learns your preferences over a 24-hour window.

---

## Next Steps

**Learn More**:
- [User Guide](docs/USER_GUIDE.md) - Comprehensive usage guide
- [Examples](docs/EXAMPLES.md) - More query examples with results
- [Architecture](docs/ARCHITECTURE.md) - How it works under the hood

**Customize**:
- [Add Your Own Data](docs/CUSTOM_DATA.md) - Connect to your database
- [Create Semantic Models](docs/SEMANTIC_MODELS.md) - Define your business metrics
- [Advanced Configuration](docs/ADVANCED.md) - Performance tuning and options

**Get Help**:
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions
- [FAQ](docs/FAQ.md) - Frequently asked questions
- [GitHub Issues](https://github.com/yourusername/claude-analyst/issues) - Report bugs

---

## Troubleshooting

### Issue: "uv: command not found"

**Cause**: UV not installed or not in PATH

**Solution**:
```bash
# Reinstall UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart your terminal, then try again
uv --version
```

### Issue: "Database file not found"

**Cause**: Database hasn't been generated

**Solution**:
```bash
cd semantic-layer
uv run python generate_sample_data.py
uv run python load_to_duckdb.py
```

### Issue: "MCP server not showing in Claude Desktop"

**Causes**:
1. Using `"command": "uv"` instead of full path to uv
2. Config file has wrong path
3. Config file has invalid JSON syntax
4. Claude Desktop not restarted

**Solution**:
```bash
# 1. Find the full path to uv
which uv
# Output: /opt/homebrew/bin/uv (or similar)

# 2. Update config to use FULL PATH:
# Change "command": "uv" to "command": "/opt/homebrew/bin/uv"

# 3. Verify config exists and has correct paths
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# 4. Validate JSON syntax at https://jsonlint.com

# 5. Quit Claude Desktop completely (Cmd+Q)
# 6. Reopen Claude Desktop
# 7. Wait 10 seconds for MCP to initialize
```

**Why this matters**: GUI apps on macOS don't inherit your shell's PATH environment variable, so they can't find `uv` unless you provide the full path.

### Issue: "Python version too old"

**Cause**: System has Python 3.10 or older

**Solution**:
```bash
# Install Python 3.11+ from python.org
# Or use pyenv:
brew install pyenv
pyenv install 3.13
pyenv global 3.13

# Verify
python3 --version
```

### Issue: "Tools appear but queries fail"

**Cause**: Database or semantic models have issues

**Solution**:
```bash
# Run the comprehensive test
cd semantic-layer
uv run python test_all_functionality.py

# Check for error messages
# If tests pass, the issue is in Claude Desktop
```

### Still Having Issues?

1. **Check logs**: Look at `semantic-layer/ai_analyst.log` for error messages
2. **Run tests**: `uv run python test_mcp_server.py` shows what's failing
3. **Ask for help**: [Open an issue](https://github.com/yourusername/claude-analyst/issues) with:
   - Your OS and Python version
   - Error messages from logs
   - Output of test commands

---

## Success Checklist

After setup, you should:

- [x] See "✅ SUCCESS: 3 models loaded" from verification test
- [x] See MCP tools indicator in Claude Desktop
- [x] Get a response when asking "List available data models"
- [x] See real data when asking "How many users do we have?"
- [x] Get statistical analysis when asking about comparisons

**If all checked**, you're ready! Start asking questions about your data.

---

## What's Next?

Now that you're set up, explore:

1. **Try the examples** in [docs/EXAMPLES.md](docs/EXAMPLES.md)
2. **Learn the workflows** - Run "comprehensive conversion analysis"
3. **Understand the data** - Review available models and metrics
4. **Ask your own questions** - The system learns from your queries

**Pro tip**: Start simple ("How many users?") and build complexity based on results. The system is designed for incremental exploration.

---

**Setup Time**: ~5 minutes
**Questions Answered**: Unlimited
**Statistical Rigor**: Automatic

**Happy analyzing!** 📊
