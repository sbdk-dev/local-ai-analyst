# General Data Science Project Configuration

## 🚨🚨🚨 CRITICAL: PREVENT DATA FABRICATION 🚨🚨🚨

### NEVER FABRICATE OBSERVATIONS - EXECUTION ERROR PREVENTION

**MANDATORY WORKFLOW:**
1. **Build Code** - Write ONLY code, no observations
2. **Execute Code** - Run with `uv run python`, capture EXACT output
3. **Annotate Reality** - Write observations ONLY after seeing real output

**VIOLATION = PROJECT FAILURE**

**Example Error Pattern:**
- Code: `df['column'].value_counts()`
- Real Output: `A: 150, B: 120, C: 30`
- ❌ Fabricated: "A is most common, C barely represented"
- ✅ Correct: "A leads with 150, B close behind at 120"

---

## 🚨 CRITICAL EXECUTION RULES

### Absolute Mandates
1. **INCREMENTAL CELL-BY-CELL WORKFLOW** - ONE task per notebook cell
2. **TEST BEFORE NOTEBOOK** - `uv run python` verification required
3. **SHOW EXPLORATORY PROCESS** - document pivots, failures, questions
4. **NEVER FABRICATE OBSERVATIONS** - Execute first, observe second
5. **NATURAL LANGUAGE** - typing notes to yourself, not presenting

---

## 🔬 THE THREE-PHASE NOTEBOOK DEVELOPMENT (PREVENTS FABRICATION)

### Phase 1: Build Code Cells Only
- Write exploratory code cells
- Test each with `uv run python -c "code"` to verify it works
- Add code cells to notebook
- **DO NOT add observations yet** - you haven't seen the output!

### Phase 2: Execute the Notebook
- Run all cells: `uv run jupyter nbconvert --execute notebook.ipynb`
- OR open in VSCode and run cells manually
- Outputs are now stored in the .ipynb file

### Phase 3: Add Observations
- Read the executed notebook
- See what the actual outputs were
- Add markdown cells with observations based on REAL outputs
- Reference specific numbers that appeared

---

## 🧠 THE "TYPING AS YOU THINK" PATTERN

Each cell should look like a single thought you typed, then ran, then observed the output.

**Natural flow example:**
```
Cell: df.shape
Output: (1000, 15)
Next cell markdown: "1000 rows, 15 columns"

Cell: df['category'].value_counts()
Output: Type_A 450, Type_B 350, Type_C 200
Next cell markdown: "3 categories. Type_A largest (450)"
```

**Learning from output pattern:**
```
Cell: df['user_id'].nunique()
Output: 847
Next cell markdown: "847 unique users. Less than total rows - some repeat customers"
Cell: # Let me check this...
```

---

## ❌ FORBIDDEN BEHAVIORS

- Planning 10 cells ahead based on requirements
- Writing polished, presentation-ready analysis on first pass
- Jumping to sophisticated models without basic EDA
- Hiding exploratory work that didn't yield insights
- Batching multiple operations in one cell without checking intermediate results
- **Making it too perfect** - formatted tables, highlighted bullets, clear ordered lists
- **Skipping interesting exploration** - only answering requirements
- **Artificial language** - "Upon analyzing...", "The findings indicate..."

---

## ✅ REQUIRED BEHAVIORS

- Start with `.head()`, `.info()`, `.describe()` on new data
- Check for nulls, duplicates, date ranges, unique values
- Plot distributions BEFORE aggregating
- Verify assumptions with print statements
- Document thought process: "Checking if...", "Unexpected..."
- Show messy exploration (failures, pivots, dead-ends)
- Test code with `uv run python` BEFORE adding to notebook
- **Add visualizations** - plots that inform decisions
- **Show dead ends** - "tried X but it didn't work", pivots
- **Make it realistic** - show actual exploration process

---

## 🗣️ NATURAL LANGUAGE GUIDELINES

**Write like you're typing notes to yourself during analysis, not presenting findings.**

**Natural notebook observations:**
```
✅ "1000 rows, 15 columns"
✅ "3 categories. Type_A largest"
✅ "Big spike in March"
✅ "Correlation is 0.73. Pretty strong"
✅ "p = 0.003. Significant"
✅ "Weird outlier at row 847"
```

**Artificial/polished style (FORBIDDEN):**
```
❌ "What I found:" or "What I learned:"
❌ "Upon analyzing the data, I discovered..."
❌ "The findings indicate that..."
❌ "It is interesting to note that..."
❌ "Let me check if..." → just do it
```

**Key principle**: Shortest natural phrasing. Drop "So", "and", "That's", "It is".

---

## 📊 VISUALIZATION GUIDELINES

**Natural Exploratory Plots:**
```python
✅ plt.hist(data)  # Simple exploration
✅ df.value_counts().plot(kind='bar')  # Quick distribution
✅ plt.scatter(x, y)  # Relationship check

❌ fig, axes = plt.subplots(2,2, figsize=(12,8))  # Over-engineered first look
❌ sns.set_style('whitegrid')  # Polished styling on first plot
❌ plt.title('Comprehensive Analysis of...')  # Formal titles
```

**Natural Plot Progression:**
```python
# Cell 1: Quick look
plt.hist(response_time)

# Cell 2 (markdown): "Most responses under 500ms"

# Cell 3: By category?
for cat in categories:
    subset = data[data['category'] == cat]['response_time']
    plt.hist(subset, alpha=0.5, label=cat)
plt.legend()

# Cell 4 (markdown): "Category A much faster"
```

---

## 🧪 STATISTICAL TESTING PATTERNS

**Natural Statistical Exploration:**
```python
# Is this difference real?
from scipy.stats import ttest_ind

# Cell 1: Set up the test
group_a = data[data['group'] == 'A']['metric']
group_b = data[data['group'] == 'B']['metric']

# Cell 2: Run test
stat, p = ttest_ind(group_a, group_b)
print(f'p = {p:.3f}')

# Cell 3 (markdown): "p = 0.012. Significant difference"
```

**Sample Size Checks:**
```python
# Check if we have enough data
data.groupby('category').size()
# Next cell: "Smallest group: 89 samples. Should be enough"
```

---

## 🔧 PYTHON ENVIRONMENT

### Required Setup
- **ALWAYS use `uv`** for Python operations
- `uv run python` for testing cells
- `uv pip install` for dependencies
- Use `uv run jupyter nbconvert --execute notebook.ipynb` to execute notebooks

### Testing Protocol
```bash
# ALWAYS test before adding to notebook
uv run python -c "import pandas as pd; print(pd.__version__)"

# Test cell code
uv run python -c "
import pandas as pd
df = pd.read_csv('data.csv')
print(df.head())
"

# If successful → add to notebook
# If error → fix, retest, then add
```

### Execution Workflow
```bash
# Execute notebook to generate outputs
uv run jupyter nbconvert --execute --to notebook --inplace notebook.ipynb

# Or execute and create new file
uv run jupyter nbconvert --execute notebook.ipynb --output executed_notebook.ipynb
```

---

## 📁 PROJECT ORGANIZATION

### Directory Structure
```
project/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   ├── exploratory/
│   └── analysis.ipynb  ← Main notebook
├── scripts/
│   └── build_notebook.py  ← Optional builder scripts
└── CLAUDE.md          ← This config
```

### Single Notebook Approach
Keep it simple: one main notebook showing the entire analysis journey from raw data to insights.

### Builder Scripts (Optional)
Builder scripts can help automate notebook construction for reproducibility:
- Use for programmatically adding cells in a specific order
- Useful when rebuilding notebooks from scratch
- Should only contain notebook structure, NOT observations (observations come after execution)
- Keep simple: `add_code()`, `add_markdown()` helper functions

---

## 🎯 SUCCESS CRITERIA

A successful data science analysis:
- ✅ Shows realistic, incremental exploration process
- ✅ All observations reference actual executed outputs
- ✅ Includes dead-ends and pivots (realistic workflow)
- ✅ Natural language throughout (not polished presentation)
- ✅ Statistical rigor where appropriate
- ✅ Clear insights grounded in evidence
- ✅ Cells run from top to bottom (reproducibility)
- ✅ Imports at top, proper dependency order
- ✅ Logical narrative flow between sections

---

## 🎨 STYLE REFERENCE

**Natural exploration pattern:**
- Start simple (load, inspect, describe)
- Print intermediate results frequently
- Ask questions during exploration
- Show calculations that inform next steps
- Document pivots when assumptions invalidated
- Use visualizations to understand before aggregating
- Natural, conversational observations

**Remember**: Show how you ACTUALLY work through data problems, not just polished results.

---

## 🛡️ ERROR PREVENTION CHECKLIST

Before adding any observation to notebook:
- [ ] Did I execute the code first?
- [ ] Am I referencing the exact output I saw?
- [ ] Am I using natural language (not formal presentation)?
- [ ] Does this look like a real note I'd type to myself?

**When in doubt**: Execute again to verify the output is what you think it is.

---

## 🔄 REPRODUCIBILITY BEST PRACTICES

### Cell Execution Order
- **CRITICAL**: Cells must run from top to bottom without errors
- Never run cells out of order during development
- Delete and restart kernel if you accidentally run out of order
- Test full execution: `jupyter nbconvert --execute notebook.ipynb`

### Code Organization Within Notebook
- **Imports at top**: All imports in first code cell
- **Constants/config second**: File paths, settings, display options
- **Functions before use**: Define helper functions before calling them
- **Linear dependency**: Each cell should depend only on cells above it

### Version Control Considerations
- Git tracks notebooks, but diffs are hard to read in .ipynb format
- Consider using `nbdime` for better notebook diffs
- Alternatively, use builder scripts (Python files) for reproducible construction
- Clear all outputs before committing: `jupyter nbconvert --clear-output notebook.ipynb`

### Documentation Standards
- Use markdown headers (##, ###) for section structure
- Each section should have narrative context
- Explain WHY you're doing analysis, not just WHAT
- Document assumptions and limitations
- Note data quality issues discovered

---

## 📝 CELL CONTENT GUIDELINES

### Code Cells
- **One logical unit per cell**: Don't combine unrelated operations
- **Show intermediate results**: Use print() to verify assumptions
- **Keep cells short**: Generally 5-15 lines max for readability
- **Comment sparingly**: Code should be self-explanatory; use markdown for explanations
- **Avoid complex nested logic**: Break into multiple cells if needed

### Markdown Cells
- **Short observations**: 1-3 sentences per cell typical
- **No headers inside observations**: Use separate header cells
- **Direct statements**: "Tech has 69% approval" not "The data shows that..."
- **Reference specific numbers**: From actual outputs above
- **Natural progression**: Each observation flows from the cell above it

### Antipatterns to Avoid
❌ Giant cell with 50+ lines doing multiple unrelated things
❌ Running same analysis multiple times with slight variations (use functions)
❌ Long print statements outputting tables (use dataframe display)
❌ Markdown cells with excessive formatting (bold, italics, colors)
❌ Code cells with no output (unless deliberate setup)

---

**End of Configuration**

*Use this configuration for any data science project to maintain authentic exploration workflow and prevent fabricated observations.*