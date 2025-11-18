# Quick Start - AI Analyst in 5 Minutes

Get the AI Analyst running and ask your first question in under 5 minutes.

---

## Prerequisites

Before starting, make sure you have:

- **Claude Desktop** OR **ChatGPT Desktop** (or both!)
  - Claude Desktop → [Download here](https://claude.ai/download)
  - ChatGPT Desktop → [Download here](https://help.openai.com/en/articles/9275200-chatgpt-desktop-app)
- **Python 3.10 or higher** installed
  ```bash
  # Check your version
  python3 --version
  # Should show: Python 3.10.x or higher
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
git clone https://github.com/sbdk-dev/claude-analyst.git
cd claude-analyst/semantic-layer

# Install dependencies (this creates a virtual environment and installs everything)
uv sync

# Verify installation
uv run python -c "print('Installation successful!')"
```

**Expected output**: `Installation successful!`

---

## Step 3: Choose Your AI Desktop

### Option A: Claude Desktop Setup

#### Automatic Setup (macOS only)

```bash
# Run the setup script (creates config with absolute path)
./scripts/setup_claude_desktop.sh
```

**Expected output**:
```
Claude Desktop configured!
Config location: ~/Library/Application Support/Claude/claude_desktop_config.json
Restart Claude Desktop to activate
```

#### Manual Setup (All Platforms)

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

   **Important**:
   - Use the **full path** to `uv` (from `which uv`)
   - Use the **full path** to your semantic-layer directory (from `pwd`)
   - GUI apps don't inherit your shell's PATH, so `"command": "uv"` won't work

5. **Save the file** (make sure it's valid JSON - no trailing commas!)

6. **Restart Claude Desktop** and proceed to Step 4.

---

### Option B: ChatGPT Desktop Setup

1. **Set your OpenAI API key**:
   ```bash
   export OPENAI_API_KEY="sk-your-key-here"
   ```

   To make this permanent, add it to your shell profile:
   ```bash
   echo 'export OPENAI_API_KEY="sk-your-key-here"' >> ~/.zshrc
   source ~/.zshrc
   ```

2. **Start the OpenAI API server**:
   ```bash
   cd semantic-layer
   uv run python run_openai_server.py
   ```

   **Expected output**:
   ```
   AI Analyst OpenAI API Server
   Starting server on http://localhost:8000
   ```

3. **Configure ChatGPT Desktop**:
   - Open ChatGPT Desktop
   - Go to Settings → Beta Features → Enable "Actions"
   - Add a new Custom Action:
     - **Name**: AI Analyst
     - **URL**: `http://localhost:8000`
     - **Auth**: None (or Bearer token if you set one)

4. **Test it**: In ChatGPT, ask "List available data models"

**Note**: Keep the terminal running while using ChatGPT Desktop. The server needs to be active.

---

## Step 4: Verify Setup

Before using your AI desktop, verify everything works locally:

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
    print(f'SUCCESS: {len(models)} models loaded')
    print(f'Available: {[m[\"name\"] for m in models]}')
asyncio.run(test())
"
```

**Expected output**:
```
SUCCESS: 3 models loaded
Available: ['users', 'events', 'engagement']
```

**If you see this**, you're ready! If not, see [Troubleshooting](#troubleshooting) below.

---

## Step 5: Start Using It

### For Claude Desktop Users

1. **Restart Claude Desktop** (Cmd+Q on Mac, then reopen)
2. **Wait 5 seconds** for the MCP server to initialize
3. **Try your first query**:
   ```
   List available data models
   ```

### For ChatGPT Desktop Users

1. **Make sure the server is running** (from Step 3)
2. **Open ChatGPT Desktop**
3. **Try your first query**:
   ```
   List available data models
   ```

**Expected response**: Both will list the 3 semantic models (users, events, engagement).

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

### Issue: "ChatGPT server won't start"

**Cause**: Missing OpenAI API key or port already in use

**Solution**:
```bash
# Check API key is set
echo $OPENAI_API_KEY
# Should show your key (not empty)

# If port 8000 is in use, kill the process
lsof -i :8000
kill -9 <PID>

# Restart server
uv run python run_openai_server.py
```

### Issue: "Python version too old"

**Cause**: System has Python 3.9 or older

**Solution**:
```bash
# Install Python 3.10+ from python.org
# Or use pyenv:
brew install pyenv
pyenv install 3.12
pyenv global 3.12

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
# If tests pass, the issue is in your AI desktop
```

### Still Having Issues?

1. **Run tests**: `uv run python test_all_functionality.py` shows what's failing
2. **Ask for help**: [Open an issue](https://github.com/sbdk-dev/claude-analyst/issues) with:
   - Your OS and Python version
   - Error messages from tests
   - Which desktop app you're using

---

## Success Checklist

After setup, you should:

- [x] See "SUCCESS: 3 models loaded" from verification test
- [x] Get a response when asking "List available data models"
- [x] See real data when asking "How many users do we have?"
- [x] Get statistical analysis when asking about comparisons

**If all checked**, you're ready! Start asking questions about your data.

---

## What's Next?

Now that you're set up, explore:

1. **Try the examples** - Ask "Run a comprehensive conversion analysis"
2. **Learn the workflows** - Ask "What workflows are available?"
3. **Understand the data** - Ask "Describe the users model"
4. **Ask your own questions** - The system learns from your queries

**Pro tip**: Start simple ("How many users?") and build complexity based on results. The system is designed for incremental exploration.

---

**Setup Time**: ~5 minutes
**Questions Answered**: Unlimited
**Statistical Rigor**: Automatic

**Happy analyzing!**
