# Mercury Data Science Take-Home - Claude Flow ML Configuration

## 🚨🚨🚨 CRITICAL: PREVENT DATA FABRICATION 🚨🚨🚨

### NEVER FABRICATE OBSERVATIONS - EXECUTION ERROR PREVENTION

**MERCURY PROJECT LESSON: I fabricated observations without executing code first**

**SPECIFIC ERRORS MADE:**
- Said "Bank Account most active" but actual output showed "Debit Card 17120, Bank Account 5591"
- Said "p < 0.001" but actual p-value was 0.005
- Said "19 days median" but actual output was 18.0

**MANDATORY WORKFLOW:**
1. **Build Code** - Write ONLY code, no observations
2. **Execute Code** - Run with `uv run python`, capture EXACT output
3. **Annotate Reality** - Write observations ONLY after seeing real output

**VIOLATION = PROJECT FAILURE**

---

## 🚨 CRITICAL EXECUTION RULES

### Absolute Mandates
1. **INCREMENTAL CELL-BY-CELL WORKFLOW** - ONE task per notebook cell
2. **ALL operations MUST be concurrent/parallel** when independent
3. **NEVER save files to root** - use organized subdirectories
4. **TEST BEFORE NOTEBOOK** - `uv run python` verification required
5. **SHOW EXPLORATORY PROCESS** - document pivots, failures, questions
6. **NEVER FABRICATE OBSERVATIONS** - Execute first, observe second

### Golden Rule: "1 MESSAGE = ALL RELATED OPERATIONS"
**Batch everything:**
- TodoWrite: ALL todos in ONE call (8-12+ for ML pipelines)
- Task tool: ALL agents spawned in ONE message
- File ops: ALL reads/writes/edits in ONE message
- Bash: ALL terminal operations in ONE message
- Memory: ALL store/retrieve in ONE message

---

## Project Context

**Candidate**: Matt Strautmann
**Company**: Mercury (B2B banking for startups)
**Role**: Data Science Manager
**Time Limit**: 5 hours maximum
**Working Directory**: `/Users/mattstrautmann/Documents/takehomes/mercury`
**Data Directory**: `Data_Science_Manager_Take_Home/`

### Assignment Structure

**Part 1: Exploratory Analysis**
- Investigate customer onboarding and product adoption patterns
- Identify 3-5 key insights for Experiences product team
- Design dashboard/app concept for self-serve exploration

**Part 2: Experiment Design**
- Design A/B test for industry-specific product recommendations
- Ground all decisions in Part 1 findings
- Address: segmentation strategy, statistical design, analysis plan, decision framework

### Deliverable Format
Jupyter notebook showing **realistic, incremental data science workflow** - NOT polished presentation

---

## 🎯 ML/Data Science Agent Orchestration

### Available Specialized Agents

**Data Science Core:**
- `data-scientist` - Statistical analysis, feature engineering, EDA
- `ml-researcher` - Research patterns, benchmark analysis, methodology
- `data-engineer` - ETL, data validation, pipeline optimization
- `model-validator` - Statistical testing, experiment design, A/B testing

**Development Support:**
- `coder` - Python implementation, notebook cell development
- `tester` - Unit tests, integration tests, statistical test validation
- `reviewer` - Code quality, statistical rigor, analysis validity
- `researcher` - Domain research, industry benchmarks, best practices

**Specialized Analysis:**
- `perf-analyzer` - Performance metrics, bottleneck analysis
- `code-analyzer` - Code structure, optimization opportunities

### Agent Execution Pattern

**Step 1: Optional Coordination Setup** (for complex multi-phase work)
```javascript
[Single Message - MCP Coordination]:
  mcp__claude-flow__swarm_init { topology: "hierarchical", maxAgents: 6 }
  mcp__claude-flow__agent_spawn { type: "data-scientist" }
  mcp__claude-flow__agent_spawn { type: "ml-researcher" }
  mcp__claude-flow__agent_spawn { type: "model-validator" }
```

**Step 2: REQUIRED - Claude Code Task Tool Spawns Real Agents**
```javascript
[Single Message - Parallel Agent Execution]:
  Task("Data Understanding", "Load and explore 3 datasets. Check shapes, dtypes, nulls, distributions. Document findings.", "data-scientist")
  Task("Research Background", "Research B2B fintech onboarding best practices and A/B testing frameworks.", "ml-researcher")
  Task("Validation Planning", "Design statistical tests for approval rates, product adoption, churn analysis.", "model-validator")

  // Batch ALL todos (8-12 minimum for ML work)
  TodoWrite { todos: [
    {content: "Load organizations.csv and inspect", status: "in_progress", activeForm: "Loading organizations data"},
    {content: "Load adoption_funnel.csv and inspect", status: "pending", activeForm: "Loading funnel data"},
    {content: "Load product_usage.csv and inspect", status: "pending", activeForm: "Loading usage data"},
    {content: "Calculate funnel conversion rates", status: "pending", activeForm: "Calculating conversions"},
    {content: "Analyze industry × approval patterns", status: "pending", activeForm: "Analyzing industry patterns"},
    {content: "Analyze segment × product adoption", status: "pending", activeForm: "Analyzing adoption patterns"},
    {content: "Define and measure churn", status: "pending", activeForm: "Measuring churn"},
    {content: "Synthesize 3-5 key insights", status: "pending", activeForm: "Synthesizing insights"},
    {content: "Design dashboard concept", status: "pending", activeForm: "Designing dashboard"},
    {content: "Design experiment methodology", status: "pending", activeForm: "Designing experiment"},
    {content: "Calculate sample size requirements", status: "pending", activeForm: "Calculating sample size"},
    {content: "Define decision framework", status: "pending", activeForm: "Defining decisions"}
  ]}

  // Parallel file operations
  Bash "mkdir -p notebooks/exploratory analysis/figures docs/insights"
  Read "Data_Science_Manager_Take_Home/organizations.csv"
  Read "Data_Science_Manager_Take_Home/adoption_funnel.csv"
  Read "Data_Science_Manager_Take_Home/product_usage.csv"
```

---

## 📊 Dataset Schema & Relationships

### 1. organizations.csv (~500 rows)
```python
Columns:
- organization_id (PK)        # Unique identifier
- industry                    # Specific industry (granular)
- industry_type               # Broader category
- segment_size                # micro | small | medium
- segment_growth_potential    # low | high
```

### 2. adoption_funnel.csv (~2,000 rows)
```python
Columns:
- organization_id (PK)        # Links to organizations
- funnel_stage (PK)           # application_submitted | approved | first_deposit | first_active
- date                        # When stage completed (nullable)

Notes:
- Long format: each org has 0-4 rows (one per stage reached)
- first_active = 2+ transactions in 30 days
```

### 3. product_usage.csv (~200,000 rows)
```python
Columns:
- organization_id (PK)        # Links to organizations
- day (PK)                    # Date of activity
- product (PK)                # Bank Account | Debit Card | Credit Card | Invoicing
- is_active                   # Active in last 30 days (2+ txns for Bank, 1+ for others)

Notes:
- Daily grain: org × day × product
- All orgs get Bank Account when approved
- Credit Card has eligibility restrictions
```

### Relationship Map
```
organizations (500)
    ↓ (1:many)
adoption_funnel (2,000) - multiple stages per org
    ↓ (1:many)
product_usage (200,000) - daily product activity per org
```

**Join Key**: `organization_id` across all tables

**File Locations**:
```
/Users/mattstrautmann/Documents/takehomes/mercury/Data_Science_Manager_Take_Home/
  ├── organizations.csv
  ├── adoption_funnel.csv
  └── product_usage.csv
```

---

## 🔬 Incremental Development Workflow - MANDATORY

### THE THREE-PHASE NOTEBOOK DEVELOPMENT (PREVENTS FABRICATION)

**Phase 1: Build Code Cells Only**
- Write exploratory code cells
- Test each with `uv run python -c "code"` to verify it works
- Add code cells to notebook
- **DO NOT add observations yet** - you haven't seen the output!

**Phase 2: Execute the Notebook**
- Run all cells in sequence using `uv run jupyter nbconvert --execute`
- OR open in VSCode and run cells manually
- Outputs are now stored in the .ipynb file

**Phase 3: Add Observations**
- Read the executed notebook
- See what the actual outputs were
- Add markdown cells with observations based on REAL outputs
- Reference specific numbers that appeared

### THE "TYPING AS YOU THINK" PATTERN

Each cell should look like a single thought you typed, then ran, then observed the output.

**Natural flow example:**
```
Cell: orgs.shape
Output: (500, 5)
Next cell markdown: "500 orgs"
Next cell: orgs['industry_type'].value_counts()
Output: E-commerce 223, Technology 153, etc.
Next cell markdown: "3 main industry types"
```

### FORBIDDEN BEHAVIORS ❌
- Planning 10 cells ahead based on assignment questions
- Writing polished, presentation-ready analysis on first pass
- Jumping to sophisticated models without basic EDA
- Hiding exploratory work that didn't yield insights
- Batching multiple operations in one cell without checking intermediate results
- Using placeholders, TODOs, or mock implementations
- **Making it too perfect** - formatted tables, highlighted bullets, clear ordered lists
- **Skipping interesting exploration** - only answering assignment questions
- **Citing research stats** - use research to guide questions, don't reference it

### REQUIRED BEHAVIORS ✅
- Start with `.head()`, `.info()`, `.describe()` on new data
- Check for nulls, duplicates, date ranges, unique values
- Plot distributions BEFORE aggregating
- Verify assumptions with print statements
- Document thought process: "Checking if...", "Unexpected..."
- Show messy exploration (failures, pivots, dead-ends)
- Test code with `uv run python` BEFORE adding to notebook
- Natural, conversational markdown (not polished presentation)
- **Add visualizations** - plots that inform decisions
- **Test hypotheses from research** - without citing the research
- **Show dead ends** - "tried X but it didn't work", pivots
- **Make it realistic** - this should look like 5 hours of real work

### NATURAL LANGUAGE GUIDELINES

**Write like you're typing notes to yourself during analysis, not presenting findings.**

**Natural notebook observations:**
```
✅ "500 orgs"
✅ "3 main industry types"
✅ "Big drop from approval to activation"
✅ "Tech way higher on Credit Card (13% vs 3%)"
✅ "Median 18 days to activate"
✅ "p = 0.005. Significant"
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

### VISUALIZATION GUIDELINES

**Natural Exploratory Plots:**
```python
✅ plt.hist(approval_days)  # Simple exploration
✅ org_approval.value_counts().plot(kind='bar')  # Quick distribution
✅ plt.scatter(x, y)  # Relationship check

❌ fig, axes = plt.subplots(2,2, figsize=(12,8))  # Over-engineered first look
❌ sns.set_style('whitegrid')  # Polished styling on first plot
❌ plt.title('Distribution of Approval Days by Industry Type')  # Formal titles
```

### STATISTICAL TESTING PATTERNS

**Natural Statistical Exploration:**
```python
# Is this difference real?
from scipy.stats import chi2_contingency

# Cell 1: Set up the test
tech_cc = adoption[adoption['industry_type'] == 'Technology']['adopted_cc'].sum()
other_cc = adoption[adoption['industry_type'] != 'Technology']['adopted_cc'].sum()

# Cell 2: Run test
chi2, p = chi2_contingency([[tech_yes, tech_no], [other_yes, other_no]])[:2]
print(f'p = {p:.3f}')

# Cell 3 (markdown): "p = 0.005. Significant"
```

### Cell-by-Cell Protocol

**Every code cell follows this workflow:**

1. **Draft** - Write exploration code for ONE specific task
2. **Test** - Execute with `uv run python -c "..."` to verify
3. **Add** - Once working, add cell to notebook
4. **Execute** - Run cell in notebook, inspect output
5. **Decide** - Based on output, determine next exploration step
6. **Repeat** - Continue incremental discovery

**Example:**
```bash
# Step 1: Test the code
uv run python -c "
import pandas as pd
df = pd.read_csv('Data_Science_Manager_Take_Home/organizations.csv')
print(df.shape)
print(df.info())
"

# Step 2: If it works, add to notebook as new cell
# Step 3: Execute in notebook and inspect
# Step 4: Based on output, decide: "Let me check industry distribution next..."
```

---

## 🧬 SPARC Methodology for Data Science

### Phase 1: Specification (Data Understanding)
**Goal**: Build foundational understanding of each dataset independently

**Organizations Dataset Exploration:**
```python
# Cell 1: Load and inspect
import pandas as pd
orgs = pd.read_csv('Data_Science_Manager_Take_Home/organizations.csv')
print(orgs.shape)
print(orgs.info())

# Cell 2: Check for nulls
print(orgs.isnull().sum())

# Cell 3: Industry type distribution
print(orgs['industry_type'].value_counts())

# Cell 4: Specific industry breakdown
print(orgs.groupby('industry_type')['industry'].nunique())

# Cell 5: Segment breakdown
print(pd.crosstab(orgs['segment_size'], orgs['segment_growth_potential']))
```

**TodoWrite Pattern for Phase 1:**
```json
{
  "todos": [
    {"content": "Load organizations.csv", "status": "completed", "activeForm": "Loading organizations"},
    {"content": "Check orgs nulls and dtypes", "status": "completed", "activeForm": "Checking data quality"},
    {"content": "Explore industry_type distribution", "status": "in_progress", "activeForm": "Exploring industries"},
    {"content": "Explore industry granularity", "status": "pending", "activeForm": "Checking industry detail"},
    {"content": "Analyze segment combinations", "status": "pending", "activeForm": "Analyzing segments"},
    {"content": "Load adoption_funnel.csv", "status": "pending", "activeForm": "Loading funnel data"},
    {"content": "Verify funnel stages", "status": "pending", "activeForm": "Verifying stages"},
    {"content": "Check date ranges and nulls", "status": "pending", "activeForm": "Checking dates"},
    {"content": "Calculate stage conversion rates", "status": "pending", "activeForm": "Calculating conversions"},
    {"content": "Load product_usage.csv", "status": "pending", "activeForm": "Loading usage data"},
    {"content": "Check date range and products", "status": "pending", "activeForm": "Checking usage data"},
    {"content": "Analyze active vs inactive", "status": "pending", "activeForm": "Analyzing activity"}
  ]
}
```

### Phase 2: Pseudocode (Analysis Planning)
**Goal**: Outline analytical approaches before implementing

**Industry × Approval Analysis Pseudocode:**
```python
# Markdown cell: "Let me think through how to measure approval rates..."

"""
Approach for industry approval analysis:

1. Join organizations + adoption_funnel
2. For each org, check if 'approved' stage exists
3. Calculate approval_rate = approved_orgs / total_orgs
4. Group by industry_type, then by industry
5. Check sample sizes (need n>30 for statistical validity)
6. Visualize with confidence intervals
"""

# Then implement ONE step at a time in subsequent cells
```

### Phase 3: Architecture (Data Pipelines)
**Goal**: Design joins and analytical workflows

**Join Strategy:**
```python
# Cell: Base data assembly
# "Starting with organizations as base, left join funnel stages..."

import pandas as pd

orgs = pd.read_csv('Data_Science_Manager_Take_Home/organizations.csv')
funnel = pd.read_csv('Data_Science_Manager_Take_Home/adoption_funnel.csv')

# Pivot funnel to wide format (one row per org)
funnel_wide = funnel.pivot(
    index='organization_id',
    columns='funnel_stage',
    values='date'
)

# Join to organizations
df = orgs.merge(funnel_wide, on='organization_id', how='left')
print(df.shape)
print(df.columns)
```

### Phase 4: Refinement (Iterative Analysis)
**Goal**: Test hypotheses, iterate based on findings

**Exploration Pattern:**
```python
# Cell: "Let me check if approval rates differ by industry_type..."
approval_by_industry = df.groupby('industry_type').agg(
    total_orgs=('organization_id', 'count'),
    approved_orgs=('approved', 'count')
)
approval_by_industry['approval_rate'] = (
    approval_by_industry['approved_orgs'] / approval_by_industry['total_orgs']
)
print(approval_by_industry)

# Markdown: "Hmm, Technology has 78% approval but only 15 orgs.
# Let me check if this is statistically meaningful..."

# Next cell: Statistical significance check
from scipy.stats import chi2_contingency
# ... implement test
```

### Phase 5: Completion (Insights & Experiment Design)
**Goal**: Synthesize findings and design rigorous experiment

**Insights Documentation:**
```markdown
## Key Finding #1: Industry-Specific Product Preferences

**Data**: Analyzed product adoption patterns across 12 industry_types and 500 orgs.

**Finding**: E-commerce orgs adopt Invoicing 2.3x faster than baseline (p<0.01, n=47).

**Implication**: Strong signal for featuring Invoicing to e-commerce during onboarding.

**Confidence**: High - 47 orgs, effect size = +23 percentage points, p=0.003
```

**Experiment Design Template:**
```markdown
## Experiment: Industry-Specific Product Recommendations

### Hypothesis
Featuring products based on industry_type during onboarding will increase
7-day product adoption rate by ≥10 percentage points.

### Variants
- **Control**: Current onboarding (no featured product)
- **Treatment**: Feature product with highest adoption rate for user's industry_type

### Randomization
- **Unit**: organization_id
- **Split**: 50/50 control/treatment
- **Stratification**: By segment_size (micro, small, medium) to ensure balance

### Primary Metric
**7-day product adoption rate**: % of orgs that activate ≥1 non-Bank product
within 7 days of approval.

**Baseline**: 34% (from historical data)
**MDE**: 10 percentage points (34% → 44%)

### Sample Size
- Power: 0.8
- Alpha: 0.05 (one-sided)
- Required: ~450 orgs per group = 900 total
- Runtime: ~4 weeks (assuming 225 approvals/week)

### Guardrail Metrics
1. Approval rate (must not decrease)
2. Time to first_deposit (must not increase)
3. Time to first_active (must not increase)

### Analysis Plan
1. **Primary**: Two-sample proportion test on 7-day adoption rate
2. **Subgroup**: Analyze by industry_type (HTE detection)
3. **Guardrails**: t-tests on time metrics, chi-square on approval rate
4. **Cohort**: Survival curves for time-to-adoption

### Decision Framework
| Result | Action |
|--------|--------|
| +10pp adoption, p<0.05, all guardrails pass | Full rollout |
| +10pp for some industries only | Selective rollout |
| +5-10pp (below MDE) | Do not implement |
| Neutral or negative | Abandon, iterate design |
```

---

## 🔧 Python Environment & Tools

### Required Environment
- **Python**: `uv` package manager (ALWAYS use `uv run python`)
- **Jupyter**: Claude Desktop `jupyter` skill
- **Key Libraries**: pandas, numpy, matplotlib, seaborn, scipy, statsmodels

### Installation
```bash
uv pip install pandas numpy matplotlib seaborn scipy statsmodels jupyter
```

### Testing Protocol
```bash
# ALWAYS test before adding to notebook
uv run python -c "import pandas as pd; print(pd.__version__)"

# Test cell code
uv run python -c "
import pandas as pd
df = pd.read_csv('path/to/file.csv')
print(df.head())
"

# If successful → add to notebook
# If error → fix, retest, then add
```

---

## 📁 Project Organization

### Directory Structure
```
/Users/mattstrautmann/Documents/takehomes/mercury/
├── Data_Science_Manager_Take_Home/
│   ├── organizations.csv
│   ├── adoption_funnel.csv
│   ├── product_usage.csv
│   └── matt_strautmann_mercury_analysis.ipynb  ← SINGLE notebook (entire assignment)
├── claude-flow/
│   ├── CLAUDE.md
│   ├── coordination/
│   └── memory/
├── CLAUDE.md
└── onboarding_experimentation_research.md
```

### Single Notebook Structure (Realistic Scope)
```
matt_strautmann_mercury_analysis.ipynb  (~20-30 cells total for 5-hour assignment)

Part 1: Data Understanding (cells 1-8)
- Load 3 datasets, check shapes/dtypes/nulls
- Explore industries, segments, products
- Basic distributions, data quality checks

Part 1: Analysis (cells 9-18)
- Industry × approval rates
- Segment × product adoption
- Product churn patterns
- Key findings emerge naturally

Part 1: Insights Summary (cells 19-20)
- 3-5 key insights with evidence (n, p-value, effect size)
- Dashboard concept (brief description)

Part 2: Experiment Design (cells 21-28)
- Hypothesis (grounded in Part 1 findings)
- Segmentation choice (industry_type vs industry, with data justification)
- Sample size calculation (show work)
- Metrics and guardrails
- Decision framework (result → action mapping)
```

**Note**: One notebook, ~25 cells, natural progression. NOT 9 separate files.

---

## 🧪 Analysis Phase Breakdown

### Phase 1: Data Understanding (1-1.5 hours)

**Organizations Dataset:**
- [ ] Load, check shape, dtypes, nulls
- [ ] Distribution of industry_type (how many categories?)
- [ ] Distribution of industry within each industry_type
- [ ] Segment breakdown: size × growth_potential (2×2 or 2×3 matrix)
- [ ] Data quality issues

**Adoption Funnel Dataset:**
- [ ] Load, check shape, dtypes, nulls
- [ ] Verify funnel stages (4 expected)
- [ ] Date ranges and null dates (incomplete funnels?)
- [ ] Conversion rates between stages
- [ ] Drop-off points

**Product Usage Dataset:**
- [ ] Load, check shape, dtypes, nulls
- [ ] Date range of data
- [ ] Product breakdown (4 products expected)
- [ ] Active vs inactive distributions
- [ ] Daily grain verification

### Phase 2: Cross-Dataset Analysis (1.5-2 hours)

**Industry × Approval Rates:**
- [ ] Join organizations + adoption_funnel
- [ ] Approval rate by industry_type
- [ ] Approval rate by specific industry
- [ ] Statistical significance (sample sizes)
- [ ] Visualize top/bottom performers

**Segment × Product Adoption:**
- [ ] Join organizations + product_usage
- [ ] Product adoption rate by segment_size
- [ ] Product adoption rate by segment_growth_potential
- [ ] High growth → more products?
- [ ] Which segments adopt Credit Card vs Invoicing?

**Funnel Stage × Product Usage:**
- [ ] Time from approval to first product usage
- [ ] Orgs at first_active vs earlier stages: product adoption differences?
- [ ] Product patterns for stuck orgs

**Product Churn Analysis:**
- [ ] Define churn (active → inactive 30+ days)
- [ ] Churn rate by product
- [ ] Churn rate by industry/segment
- [ ] Time-based churn patterns (cohort analysis)

### Phase 3: Insights & Dashboard (0.5-1 hour)

**Insights Synthesis:**
- [ ] Document top 3-5 findings with data
- [ ] Prioritize by business impact
- [ ] Include confidence levels (n, significance)
- [ ] Connect insights → product actions

**Dashboard Concept:**
- [ ] Define use cases (who? what decisions?)
- [ ] Key metrics and dimensions
- [ ] Interactive filters (industry, segment, time)
- [ ] Dashboard sections (funnel, adoption, churn)
- [ ] Data refresh requirements

### Phase 4: Experiment Design (1-1.5 hours)

**Hypothesis Formation:**
- [ ] Which industries prefer which products? (from Phase 2)
- [ ] industry_type vs industry: which has stronger signal?
- [ ] Baseline adoption rates (control benchmark)
- [ ] Products with clearest industry preferences

**Experiment Design:**
- [ ] Variant selection (industry_type vs industry + justification)
- [ ] Treatment logic (which product for which industry)
- [ ] Randomization unit (organization-level)
- [ ] Control/treatment split (50/50 or other?)
- [ ] Stratification strategy (by segment? industry?)

**Sample Size & Duration:**
- [ ] Primary metric (adoption rate? time to adoption? activation?)
- [ ] Calculate MDE (minimum detectable effect)
- [ ] Required sample size per variant
- [ ] Project runtime (weekly/monthly org volume)
- [ ] Early stopping criteria

**Analysis Plan:**
- [ ] Primary metric(s) and success criteria
- [ ] Secondary/guardrail metrics
- [ ] Statistical test method (t-test, chi-square, survival?)
- [ ] Subgroup analysis plan (by segment, industry_type)
- [ ] Heterogeneous treatment effects

**Decision Framework:**
- [ ] Strong positive → full rollout
- [ ] Positive for some industries → selective rollout
- [ ] Neutral → iterate or abandon
- [ ] Negative → abandon
- [ ] Define "strong positive" threshold (+10% adoption?)
- [ ] Plan for unexpected results (helps some, hurts others)

---

## 🎯 Key Research Context (from onboarding_experimentation_research.md)

### Onboarding Best Practices
- **Minimize friction**: Reduce steps to activation
- **Personalize**: Tailor to user role/industry (Brex: +29% applications via industry segmentation)
- **Interactive elements**: Hands-on from the start
- **Onboarding checklists**: 3-5 key tasks → activation
- **Celebrate progress**: Small wins motivate exploration

### Key Metrics
- **Activation rate**: Users reaching value milestone / signups × 100
  - Median SaaS: 17% | Top performers: 65%
- **Time to Value (TTV)**: Speed to experience core value
- **Churn rate**: Top SaaS: 3-5% | Fintech: 25-40% first-year account closure

### B2B Fintech Context
- Market projected: $949B by 2028
- Critical challenge: Adjusting to different customer segments
- Growth areas: B2B(2X), embedded fintech, lending

### A/B Testing Framework

**Randomization:**
- Simple: No history needed, risk of imbalance
- Stratified: Requires cohort knowledge, prevents imbalance
  - Use when: n<400, known influential factors, group-level randomization
  - Choose 4-6 strata (industry, segment, etc.)

**Statistical Rigor:**
- Power: 0.8 (80% probability of detecting MDE)
- Significance: α=0.05 (5% false positive rate)
- MDE has DRAMATIC effect on required sample size

**Three-Pillar Decision:**
1. **Statistical significance**: Is this real? (p<0.05)
2. **Practical significance**: Does this matter? (effect size)
3. **Business impact**: Should we do this? (cost, feasibility, alignment)

**Guardrail Metrics:**
- Trust: Sample ratio mismatch, data quality
- Organizational: UX metrics, revenue, engagement
- Airbnb's approach: Impact guardrail, inferiority test, non-inferiority test

**Heterogeneous Treatment Effects (HTE):**
- Different subpopulations respond differently
- Average effects can hide important differences
- Inform selective rollout decisions

**Analysis Methods:**
- Cohort analysis: Compare retention across cohorts
- Survival analysis: Time-to-event (when do users churn/adopt?)
- Subgroup analysis: Identify HTE by industry, segment

---

## 📊 Agent Coordination Hooks

### Every Agent MUST Execute

**Before Work:**
```bash
npx claude-flow@alpha hooks pre-task --description "Data exploration of organizations.csv"
npx claude-flow@alpha hooks session-restore --session-id "mercury-takehome"
```

**During Work:**
```bash
npx claude-flow@alpha hooks post-edit --file "notebooks/exploratory/02_orgs_eda.ipynb" --memory-key "mercury/eda/organizations"
npx claude-flow@alpha hooks notify --message "Completed organizations EDA: 500 orgs, 12 industry_types, 47 industries"
```

**After Work:**
```bash
npx claude-flow@alpha hooks post-task --task-id "organizations-eda"
npx claude-flow@alpha hooks session-end --export-metrics true
```

### Memory Storage Pattern
```bash
# Store key findings
npx claude-flow@alpha memory store --key "mercury/insights/industry-approval" --value "Technology: 78% approval (n=15), E-commerce: 65% (n=47)"

# Store experiment parameters
npx claude-flow@alpha memory store --key "mercury/experiment/baseline-adoption" --value "34% 7-day adoption rate"

# Retrieve for next agent
npx claude-flow@alpha memory retrieve --key "mercury/insights/industry-approval"
```

---

## ✅ Success Criteria

This analysis succeeds when:
- ✅ All three datasets explored and understood
- ✅ 3-5 key insights identified with supporting data
- ✅ Dashboard concept clearly described
- ✅ Experiment design is data-driven and complete
- ✅ Notebook shows realistic, incremental exploration (not polished presentation)
- ✅ All code tested with `uv run python` before notebook addition
- ✅ Analysis completed within ~5 hours of focused work
- ✅ Statistical rigor: sample sizes, significance tests, confidence intervals
- ✅ Business impact: insights → actions, experiment → decisions

---

## 🎨 Style Reference

Analysis should mirror incremental, exploratory style:
- Start simple (load, inspect, describe)
- Print intermediate results frequently
- Ask questions during exploration ("Does this hold for all industries?")
- Show calculations that inform next steps
- Document pivots when assumptions invalidated
- Visualizations to understand before aggregating
- Natural, conversational markdown (not formal)

**Remember**: This is a DS Manager take-home. Show how you ACTUALLY work through ambiguous data problems, not just polished results.

---

## Important Instruction Reminders

Do what has been asked; nothing more, nothing less.
NEVER create files unless absolutely necessary.
ALWAYS prefer editing existing files to creating new ones.
NEVER proactively create documentation files (*.md) unless explicitly requested.
Never save working files, texts/mds, and tests to the root folder.

**Claude Flow coordinates strategy. Claude Code's Task tool executes with real agents.**

---

## Quick Reference Commands

```bash
# Initialize swarm (optional, for complex coordination)
npx claude-flow@alpha swarm init --topology hierarchical --max-agents 6

# Test Python cell
uv run python -c "import pandas as pd; print(pd.__version__)"

# Install dependencies
uv pip install pandas numpy matplotlib seaborn scipy statsmodels

# Create directory structure
mkdir -p notebooks/exploratory analysis/figures docs/insights

# Memory operations
npx claude-flow@alpha memory store --key "mercury/key" --value "data"
npx claude-flow@alpha memory retrieve --key "mercury/key"

# Session management
npx claude-flow@alpha hooks session-restore --session-id "mercury-takehome"
npx claude-flow@alpha hooks session-end --export-metrics true
```

---

**End of Configuration**
