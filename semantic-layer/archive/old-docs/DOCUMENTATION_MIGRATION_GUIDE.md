# Documentation Migration Guide

**Purpose**: Step-by-step guide for implementing the new documentation architecture
**Timeline**: 2-3 weeks
**Status**: Ready for Implementation

---

## Quick Start for Implementation

### Day 1: Foundation Setup

**Morning: Create Directory Structure**

```bash
cd /Users/mattstrautmann/Documents/github/claude-analyst/semantic-layer/docs

# Create main directories
mkdir -p getting-started user-guide concepts reference development deployment archive templates

# Create hub README files
touch getting-started/README.md
touch user-guide/README.md
touch concepts/README.md
touch reference/README.md
touch development/README.md
touch deployment/README.md
touch archive/README.md

echo "✓ Directory structure created"
```

**Afternoon: Write Hub READMEs**

Each hub README should contain:
1. Section overview (2-3 sentences)
2. Navigation to all documents in section
3. Quick links to most important documents
4. Cross-links to related sections

**Example Pattern** (docs/getting-started/README.md):
```markdown
# Getting Started with AI Analyst

Get up and running with AI Analyst in minutes. This section guides you from installation through your first successful analysis.

## Quick Navigation

**Start here** → [5-Minute Quick Start](00-quick-start.md)

Then continue with:
- [Installation Guide](01-installation.md) - Detailed setup
- [First Analysis](02-first-analysis.md) - Your first query
- [Understanding Results](03-understanding-results.md) - Reading outputs
- [Example Workflows](04-example-workflows.md) - Common patterns

## What's Next?

Once you're comfortable with basics:
- [User Guide](../user-guide/) - Full feature exploration
- [Concepts](../concepts/) - Understand how it works
- [Troubleshooting](../user-guide/troubleshooting.md) - Fix common issues

---

**New to data analysis?** Start with [Quick Start](00-quick-start.md)
**Experienced analyst?** Jump to [User Guide](../user-guide/)
**Need help?** Check [Troubleshooting](../user-guide/troubleshooting.md)
```

---

## Content Migration Map

### Source to Destination Mapping

**Getting Started Section**:
```
Source                           → Destination
----------------------------------------------------------------------
README.md (lines 131-175)       → getting-started/00-quick-start.md
UAT_DEPLOYMENT_GUIDE.md (L32-90) → getting-started/01-installation.md
[NEW CONTENT]                   → getting-started/02-first-analysis.md
STATISTICAL_PATTERNS.md (L1-50) → getting-started/03-understanding-results.md
PHASE_4_3_COMPLETE.md (L304-336) → getting-started/04-example-workflows.md
```

**User Guide Section**:
```
Source                           → Destination
----------------------------------------------------------------------
[NEW CONTENT]                   → user-guide/natural-language-queries.md
PHASE_4_3_COMPLETE.md (L227-290) → user-guide/analytical-workflows.md
STATISTICAL_PATTERNS.md (L115-340) → user-guide/interpreting-statistics.md
[NEW CONTENT]                   → user-guide/best-practices.md
UAT_DEPLOYMENT_GUIDE.md (L279-320) → user-guide/troubleshooting.md
```

**Concepts Section**:
```
Source                           → Destination
----------------------------------------------------------------------
CURRENT_STATE.md (L14-66)       → concepts/architecture-overview.md
SEMANTIC_MODEL_DOCUMENTATION.md → concepts/semantic-layer-explained.md
FABRICATION_PREVENTION.md       → concepts/execution-first-pattern.md
STATISTICAL_PATTERNS.md (L1-150) → concepts/statistical-rigor.md
PHASE_4_1_COMPLETE.md (L82-90)  → concepts/conversation-memory.md
```

**Reference Section**:
```
Source                           → Destination
----------------------------------------------------------------------
server.py (docstrings)          → reference/mcp-tools.md [GENERATE]
SEMANTIC_MODEL_DOCUMENTATION.md → reference/semantic-models.md
workflow_orchestrator.py        → reference/workflow-templates.md [GENERATE]
[NEW CONTENT]                   → reference/query-language.md
PERFORMANCE_SUMMARY.md          → reference/performance-benchmarks.md
```

**Development Section**:
```
Source                           → Destination
----------------------------------------------------------------------
UAT_DEPLOYMENT_GUIDE.md (L124-190) → development/setup.md
DESIGN_NOTES.md + PHASE docs    → development/architecture-deep-dive.md
SEMANTIC_MODEL_DECISIONS.md     → development/adding-semantic-models.md
PHASE_4_3_COMPLETE.md (L15-100) → development/adding-workflows.md
[EXTRACT from server.py]        → development/extending-mcp-tools.md
test_*.py patterns              → development/testing-guide.md
[NEW CONTENT]                   → development/contributing.md
```

**Deployment Section**:
```
Source                           → Destination
----------------------------------------------------------------------
docs/CLAUDE_DESKTOP_SETUP.md    → deployment/claude-desktop-setup.md
UAT_DEPLOYMENT_GUIDE.md (L121-248) → deployment/production-deployment.md
[NEW CONTENT]                   → deployment/security-guide.md
[NEW CONTENT]                   → deployment/monitoring.md
[NEW CONTENT]                   → deployment/scaling.md
```

**Archive Section**:
```
Source                           → Destination
----------------------------------------------------------------------
PHASE_3_COMPLETE.md             → archive/phase-3-completion.md
PHASE_4_1_COMPLETE.md           → archive/phase-4-1-completion.md
PHASE_4_2_COMPLETE.md           → archive/phase-4-2-completion.md
PHASE_4_3_COMPLETE.md           → archive/phase-4-3-completion.md
PHASE_4_PLAN.md                 → archive/phase-4-plan.md
INTEGRATION_TEST_*.md           → archive/integration-tests.md
DESIGN_NOTES.md                 → archive/design-decisions.md
```

---

## Migration Scripts

### Script 1: Automated File Migration

```bash
#!/bin/bash
# File: scripts/migrate_docs.sh
# Purpose: Move files to new structure

set -e

# Archive old documentation
mkdir -p docs/archive
mv PHASE_*.md docs/archive/ 2>/dev/null || true
mv INTEGRATION_TEST_*.md docs/archive/ 2>/dev/null || true
mv DESIGN_NOTES.md docs/archive/design-decisions.md 2>/dev/null || true

# Move existing docs files
mv docs/FABRICATION_PREVENTION.md docs/concepts/execution-first-pattern.md 2>/dev/null || true
mv docs/STATISTICAL_PATTERNS.md docs/concepts/statistical-rigor.md 2>/dev/null || true
mv docs/CLAUDE_DESKTOP_SETUP.md docs/deployment/claude-desktop-setup.md 2>/dev/null || true

echo "✓ Files migrated to new structure"
```

### Script 2: Generate API Documentation

```python
#!/usr/bin/env python3
# File: scripts/generate_mcp_docs.py
# Purpose: Generate MCP tools reference from server.py

import ast
import inspect
from pathlib import Path

def extract_mcp_tools(server_file: Path) -> list:
    """Extract all @mcp.tool() decorated functions"""
    with open(server_file) as f:
        tree = ast.parse(f.read())

    tools = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check for @mcp.tool() decorator
            for decorator in node.decorator_list:
                if hasattr(decorator, 'func') and hasattr(decorator.func, 'attr'):
                    if decorator.func.attr == 'tool':
                        tools.append({
                            'name': node.name,
                            'docstring': ast.get_docstring(node),
                            'parameters': [arg.arg for arg in node.args.args],
                            'line_number': node.lineno
                        })
    return tools

def generate_tool_documentation(tools: list) -> str:
    """Generate markdown documentation for all tools"""
    doc = "# MCP Tools Reference\n\n"
    doc += "Complete reference for all MCP tools in AI Analyst.\n\n"
    doc += f"**Total Tools**: {len(tools)}\n\n"
    doc += "---\n\n"

    for tool in sorted(tools, key=lambda t: t['name']):
        doc += f"## {tool['name']}\n\n"
        doc += f"{tool['docstring']}\n\n"
        doc += "**Parameters**:\n"
        for param in tool['parameters']:
            doc += f"- `{param}`\n"
        doc += "\n---\n\n"

    return doc

if __name__ == "__main__":
    server_file = Path("mcp_server/server.py")
    output_file = Path("docs/reference/mcp-tools.md")

    tools = extract_mcp_tools(server_file)
    documentation = generate_tool_documentation(tools)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(documentation)

    print(f"✓ Generated documentation for {len(tools)} MCP tools")
```

### Script 3: Validate Documentation

```python
#!/usr/bin/env python3
# File: scripts/validate_docs.py
# Purpose: Validate all documentation links and structure

from pathlib import Path
import re

def find_broken_links(docs_dir: Path) -> list:
    """Find all broken internal links"""
    broken_links = []

    for md_file in docs_dir.rglob("*.md"):
        content = md_file.read_text()

        # Find all markdown links [text](url)
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)

        for link_text, link_url in links:
            # Skip external links
            if link_url.startswith('http'):
                continue

            # Resolve relative path
            target = (md_file.parent / link_url).resolve()

            if not target.exists():
                broken_links.append({
                    'file': str(md_file.relative_to(docs_dir)),
                    'link': link_url,
                    'text': link_text
                })

    return broken_links

def validate_required_sections(docs_dir: Path, doc_type: str) -> list:
    """Ensure documents have required sections"""
    required_sections = {
        'getting-started': ['Prerequisites', 'Next Steps'],
        'concepts': ['Overview', 'How It Works'],
        'reference': ['Overview', 'Quick Reference'],
    }

    issues = []
    section_dir = docs_dir / doc_type

    if not section_dir.exists():
        return issues

    for md_file in section_dir.glob("*.md"):
        if md_file.name == "README.md":
            continue

        content = md_file.read_text()

        for required in required_sections.get(doc_type, []):
            if f"## {required}" not in content:
                issues.append({
                    'file': str(md_file.relative_to(docs_dir)),
                    'missing': required
                })

    return issues

if __name__ == "__main__":
    docs_dir = Path("docs")

    # Check broken links
    broken = find_broken_links(docs_dir)
    if broken:
        print(f"⚠ Found {len(broken)} broken links:")
        for item in broken:
            print(f"  {item['file']}: {item['link']}")
    else:
        print("✓ All internal links valid")

    # Check required sections
    for doc_type in ['getting-started', 'concepts', 'reference']:
        issues = validate_required_sections(docs_dir, doc_type)
        if issues:
            print(f"⚠ Missing sections in {doc_type}:")
            for item in issues:
                print(f"  {item['file']}: missing '{item['missing']}'")
        else:
            print(f"✓ All {doc_type} documents have required sections")
```

---

## Day-by-Day Implementation

### Day 1: Foundation (Friday)

**Tasks**:
1. Run directory creation script
2. Write all hub README files
3. Copy templates to docs/templates/
4. Create archive README explaining historical docs

**Validation**:
- [ ] All directories created
- [ ] All hub READMEs written with navigation
- [ ] Templates available for content creation

**Time**: 4-6 hours

---

### Day 2: Getting Started Content (Monday)

**Priority**: This is highest impact - gets new users productive fast

**Tasks**:
1. Create `00-quick-start.md` (extract from README, simplify)
2. Create `01-installation.md` (from UAT guide, streamline)
3. Write `02-first-analysis.md` (NEW - walkthrough first query)
4. Create `03-understanding-results.md` (from Statistical Patterns)
5. Create `04-example-workflows.md` (from Phase 4.3 examples)

**Example First Analysis Document**:
```markdown
# Your First Analysis

Learn to run your first query and understand the results.

## What You'll Do

In 10 minutes, you'll:
1. Ask a simple question in natural language
2. Get real data results with statistical validation
3. Understand what the numbers mean

## Prerequisites

- [ ] AI Analyst installed
- [ ] Claude Desktop connected
- [ ] MCP server running

## Ask Your First Question

Open Claude Desktop and type:

"What's our user breakdown by plan type?"

### What Happens

1. **Query Generation**: AI Analyst translates your question into SQL
2. **Execution**: Runs against real database
3. **Statistical Analysis**: Validates sample sizes, runs tests
4. **Interpretation**: Returns results with context

### Example Results

You'll see something like:

```
Plan Type Analysis:
- Free: 450 users (66%)
- Starter: 120 users (18%)
- Pro: 85 users (13%)
- Enterprise: 12 users (2%)

Sample sizes: ✓ All groups have sufficient data (n>10)
Statistical note: Distribution significantly different from uniform (p<0.001)
```

## Understanding the Output

**Numbers**: Real data from your database (not AI-generated)
**Percentages**: Calculated from actual counts
**Statistical validation**: Sample size checks automatic
**Confidence**: p-value shows reliability

## Try Another Query

Now try: "Is the difference in engagement between free and paid users significant?"

This will:
- Query engagement metrics by plan
- Run t-test automatically
- Calculate effect size (Cohen's d)
- Interpret practical significance

## What You've Learned

✓ How to ask questions in natural language
✓ What results look like
✓ How to interpret statistical validation
✓ Where the data comes from (real, not fabricated)

## Next Steps

- [Example Workflows](04-example-workflows.md) - More complex analyses
- [User Guide](../user-guide/) - Full feature tour
- [Understanding Statistics](03-understanding-results.md) - Statistical deep-dive
```

**Validation**:
- [ ] All 5 getting-started documents created
- [ ] Code examples tested and working
- [ ] Cross-links between documents
- [ ] Hub README updated with all links

**Time**: 6-8 hours

---

### Day 3: User Guide Content (Tuesday)

**Tasks**:
1. Write `natural-language-queries.md` (NEW)
2. Create `analytical-workflows.md` (from Phase 4.3)
3. Create `interpreting-statistics.md` (from Statistical Patterns)
4. Write `best-practices.md` (NEW)
5. Create `troubleshooting.md` (from UAT + common issues)

**Example Best Practices Document Structure**:
```markdown
# Best Practices for AI Analyst

## Query Design

### Start Simple, Add Complexity
✓ "What's our conversion rate?"
Then: "Break that down by industry"
Then: "Is that difference significant?"

### Be Specific with Dimensions
✓ "Show revenue by plan_type and industry"
✗ "Show me everything about revenue"

### Use Time Windows Wisely
✓ "Last 30 days" for trends
✓ "Last 12 months" for seasonality
✓ "Since 2023-01-01" for specific periods

## Workflow Usage

### When to Use Workflows
- Complex multi-dimensional analysis needed
- Want comprehensive insights in one shot
- Exploring new analytical area

### When to Use Single Queries
- Quick spot checks
- Iterative exploration
- Specific tactical questions

## Performance Optimization

### Leverage Caching
- Repeated queries are cached (95% hit rate)
- Slight variations may miss cache
- Use exact same parameters when possible

### Batch Related Queries
- Workflows execute steps in parallel
- Better than sequential single queries
- Automatic optimization

## Statistical Interpretation

### Sample Size Awareness
- n<30: Be cautious with conclusions
- n<10: Results unreliable
- System warns automatically

### P-Value Context
- p<0.05: Statistically significant
- But check effect size too
- Small effect + significance = may not matter practically

### Effect Size Matters
- Cohen's d > 0.8: Large effect
- Even with p<0.001, check if difference is meaningful
```

**Validation**:
- [ ] All 5 user-guide documents created
- [ ] Examples tested and verified
- [ ] Troubleshooting covers common issues
- [ ] Hub README updated

**Time**: 6-8 hours

---

### Day 4: Concepts and Reference (Wednesday)

**Tasks**:
1. Create `architecture-overview.md` (from CURRENT_STATE)
2. Create `semantic-layer-explained.md` (from Semantic docs)
3. Create `execution-first-pattern.md` (from Fabrication Prevention)
4. Create `statistical-rigor.md` (from Statistical Patterns)
5. Create `conversation-memory.md` (from Phase 4.1)
6. Run `generate_mcp_docs.py` to create MCP tools reference
7. Create `semantic-models.md` (from Semantic Model docs)
8. Create `workflow-templates.md` (extract from orchestrator)
9. Create `performance-benchmarks.md` (from Performance Summary)

**Validation**:
- [ ] All concept documents created
- [ ] All reference documents generated
- [ ] Diagrams included where helpful
- [ ] Cross-links between concepts and reference

**Time**: 8 hours

---

### Day 5: Development and Deployment (Thursday)

**Tasks**:
1. Create `setup.md` (development setup from UAT)
2. Create `architecture-deep-dive.md` (from DESIGN_NOTES + PHASEs)
3. Create `adding-semantic-models.md` (from Semantic Decisions)
4. Create `adding-workflows.md` (from Phase 4.3)
5. Create `extending-mcp-tools.md` (extract from server.py)
6. Create `testing-guide.md` (from test patterns)
7. Write `contributing.md` (NEW)
8. Move CLAUDE_DESKTOP_SETUP to deployment/
9. Create `production-deployment.md` (from UAT)
10. Write `security-guide.md`, `monitoring.md`, `scaling.md` (NEW)

**Validation**:
- [ ] Development docs enable contribution
- [ ] Deployment docs sufficient for production
- [ ] Security considerations documented

**Time**: 8 hours

---

### Day 6: Archive and Polish (Friday)

**Tasks**:
1. Move all historical docs to archive/
2. Create archive/README.md explaining history
3. Run validation scripts (links, structure)
4. Fix all broken links
5. Ensure consistent formatting
6. Update main README with new structure
7. Test all code examples
8. Final cross-link review

**Validation**:
- [ ] No broken links
- [ ] All code examples work
- [ ] Consistent formatting
- [ ] Main README points to new structure

**Time**: 6 hours

---

## Week 2: Tooling

### Day 7-8: Automation Scripts

**Tasks**:
1. Complete `generate_mcp_docs.py`
2. Complete `generate_model_docs.py`
3. Complete `generate_workflow_docs.py`
4. Complete `validate_docs.py`
5. Create `test_doc_examples.py`

### Day 9-10: CI/CD Integration

**Tasks**:
1. Add documentation validation to CI
2. Set up automated link checking
3. Configure example testing
4. Create pre-commit hooks for docs

---

## Week 3: Polish and Launch

### Day 11-12: Review and User Testing

**Tasks**:
1. Internal review of all documentation
2. Sample user testing (3 users, different personas)
3. Collect feedback
4. Identify gaps

### Day 13: Address Feedback

**Tasks**:
1. Fix identified issues
2. Add missing content
3. Clarify confusing sections

### Day 14: Launch

**Tasks**:
1. Final validation pass
2. Update CHANGELOG
3. Create launch announcement
4. Update external references

---

## Success Criteria

### Completion Checklist

**Content**:
- [ ] All 6 documentation sections complete
- [ ] All hub READMEs navigation working
- [ ] Archive properly organized with context
- [ ] Main README rewritten for new structure

**Quality**:
- [ ] Zero broken internal links
- [ ] All code examples tested and working
- [ ] Consistent formatting throughout
- [ ] Appropriate cross-linking

**Tooling**:
- [ ] Automated doc generation working
- [ ] Validation scripts functional
- [ ] CI/CD integration complete

**User Experience**:
- [ ] Time to first query <5 minutes
- [ ] Clear progression beginner to expert
- [ ] Troubleshooting covers common issues
- [ ] Search-friendly structure

---

## Rollback Plan

If migration needs to be paused:

1. Keep old documentation in place
2. New docs in docs/ directory don't break anything
3. Can continue using old README
4. Complete migration when ready

Old documentation remains functional until new documentation is complete and validated.

---

## Maintenance After Migration

**Weekly**:
- Check for broken links
- Review new GitHub issues for doc gaps

**Monthly**:
- Run documentation coverage report
- Update performance benchmarks
- Review user feedback

**Per Release**:
- Update CHANGELOG
- Update version references
- Regenerate API documentation
- Test all code examples

---

**Ready to Start?**

```bash
# Begin migration
cd /Users/mattstrautmann/Documents/github/claude-analyst/semantic-layer
./scripts/migrate_docs.sh

# Create first document
cp docs/templates/getting-started-template.md docs/getting-started/00-quick-start.md

# Start writing!
```

---

**Last Updated**: 2025-11-08
**Status**: Ready for Implementation
**Estimated Completion**: 2-3 weeks
