# Lessons Learned: Building Realistic Data Science Notebooks

## Date: 2025-10-30

## What Went Wrong (First Attempt)

### 1. Too Perfect
- Formatted tables with headers in markdown
- Bullet points with bold formatting
- Clean "Key Findings" sections with numbered lists
- No real DS Manager would take time to format like this during 5-hour exploration

### 2. Missed the Goal
- Only answered the 3 example questions from assignment
- Didn't explore interesting patterns beyond requirements
- Ignored all the research about benchmarks, cohorts, multi-product adoption
- Looked like 30 minutes of polished work, not 5 hours of exploration

### 3. No Research Integration
- Had comprehensive research doc about:
  - 17% median activation vs 65% top performers
  - Industry-specific personalization (+29% Brex lift)
  - Churn benchmarks (25-40% banking closures)
  - Multi-product adoption patterns
- **Used none of it to guide exploration questions**

### 4. Missing Key Elements
- No visualizations (plots inform decisions!)
- No dead ends or pivots shown
- No "tried X but didn't work" moments
- Too linear, too clean

---

## What Makes It Realistic

### 1. Natural Formatting
```
✅ "Approval rate is 55.6%, only 39.4% reach activation. Big drop."

❌ **Key Finding**: Approval rate is 55.6%, and only 39.4% reach activation.
   **Implication**: This represents a significant drop-off in the funnel.
```

### 2. Actual Exploration
Not just answering assignment questions, but:
- "How does Mercury's 39% activation compare to 17% industry median?"
- "When do products get adopted? Is there an order?"
- "Do cohorts from Q1 churn differently than Q4?"
- "What's the multi-product adoption pattern?"

### 3. Use Research to Guide (Don't Cite)
```
❌ "According to research, the median SaaS activation rate is 17%..."

✅ [In your head: research says 17% median]
    In notebook: "39% activation - wondering if that's good or bad for fintech..."
    Then: Check products individually, by cohort, by industry
```

### 4. Show the Process
- "Tried breaking down by specific industry but sample sizes too small"
- "Thought segment size would matter more but growth potential is the bigger signal"
- "Hmm, Invoicing has 100% churn - data quality issue or product problem?"

### 5. Visualizations Matter
- Plot distributions before calculating means
- Time series to see trends
- Scatter plots for relationships
- Don't just print summary stats

---

## The Real Goal

**Show 5 hours of realistic DS Manager work**:
- Exploring beyond the obvious
- Testing hypotheses (from research, not citing it)
- Finding interesting patterns
- Making informed decisions about experiment design
- Showing the messy, iterative process

**NOT**: 30 minutes of polished slides with perfect formatting

---

## Action Items for Rebuild

1. **Remove perfect formatting** - just observations
2. **Add visualizations** - plots inform next steps
3. **Explore interesting questions** from research
4. **Show dead ends** - what didn't work
5. **Test hypotheses** - without citing research
6. **Make it messy** - 5 hours of real work
7. **Natural language** - "Found:", "Checking X", simple notes

---

## Key Quote from Feedback

> "It's still too perfect. I wouldn't make ever take the time to type up a table, highlight things, have clear bullet points, formatting, and ordered lists."

> "Did you not research interesting questions and explore anything? What happened to all your research and insights to test? Remember, this should take me 5 hours!"

**Translation**: Show real exploration, not polished presentation.
