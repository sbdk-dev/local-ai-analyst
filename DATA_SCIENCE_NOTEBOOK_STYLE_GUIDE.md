# Data Science Notebook Style Guide

**The Ultimate Guide to Natural, Realistic Data Science Notebooks**

Based on lessons from Mercury take-home analysis and `matt_strautmann_GoFundMe_donor_ltv.ipynb` reference.

---

## Core Philosophy: "Typing as You Think"

**Goal**: Make notebooks look like 5 hours of real exploration, not 30 minutes of polished presentation.

**Key Principle**: Each cell should look like a single thought you typed, ran, then observed the output.

---

## ✅ Natural Notebook Patterns

### 1. One Thought Per Cell

**Natural flow**:
```
Cell: orgs.shape
Output: (500, 5)
Next cell (markdown): "500 orgs"

Cell: orgs['industry_type'].value_counts()
Output: E-commerce 223, Technology 153, etc.
Next cell (markdown): "3 main industry types"
```

**NOT**:
```
Cell: print(f"Shape: {orgs.shape}")
      print(f"Industry types: {orgs['industry_type'].value_counts()}")
```

### 2. Learning from Output Pattern

**Natural**:
```
Cell: products['organization_id'].nunique()
Output: 278
Next cell (markdown): "278 unique orgs. Same as approved count!"
Next cell: # Test this hypothesis
       approved_count = funnel[funnel['funnel_stage']=='approved']['date'].notnull().sum()
       print(approved_count)
```

**NOT**:
```
Cell: # Let me check if the product data matches approved orgs
      products_count = products['organization_id'].nunique()
      approved_count = funnel[funnel['funnel_stage']=='approved']['date'].notnull().sum()
      print(f"Products: {products_count}, Approved: {approved_count}, Match: {products_count==approved_count}")
```

### 3. Natural Observations

**Natural language examples**:
```
✅ "500 orgs"
✅ "3 main industry types"
✅ "790 null dates. Not everyone completes all stages"
✅ "55.6% approval rate"
✅ "Big drop from approval to activation"
✅ "Tech way higher on Credit Card (13% vs 3%)"
✅ "That's high"
✅ "Makes sense"
✅ "Interesting"
```

**NOT artificial/formal**:
```
❌ "The dataset contains 500 organizations"
❌ "Upon analyzing the data, I discovered..."
❌ "It is interesting to note that..."
❌ "The findings indicate that..."
❌ "This suggests a significant difference"
```

---

## ❌ Artificial Notebook Anti-Patterns

### 1. Too Perfect/Polished

❌ **Formatted sections**:
```markdown
## Key Findings

### 1. Industry-Specific Product Preferences Are Strong
**Finding**: Different industry types have very different product adoption patterns:
- Technology companies are 4x more likely to adopt Credit Card (13% vs 3%)
- Technology and Consulting/Marketing adopt Invoicing at 7-9% vs E-commerce at only 1%

**Implication**: Industry-specific product recommendations could significantly improve adoption.
```

✅ **Natural observations**:
```markdown
Tech way higher on Credit Card (13% vs 3%). Consulting higher on Invoicing too.

Could try featuring different products by industry during onboarding.
```

### 2. Complex Print Statements

❌ **Batched operations**:
```python
print(f"Approval rate: {approved_count/total_orgs*100:.1f}%")
print(f"Activation rate: {active_count/total_orgs*100:.1f}%")
print(f"Drop-off: {(approved_count-active_count)/approved_count*100:.1f}%")
```

✅ **Simple calculations**:
```python
approved_count / 500
# Next cell markdown: "55.6% approval rate"

197 / 500
# Next cell markdown: "39.4% activation rate. Big drop"
```

### 3. Pre-planned Analysis

❌ **Structured approach**:
```python
# Question 1: Which industries have highest approval rates?
# Question 2: Does growth potential affect product adoption?
# Question 3: What does product churn look like?
```

✅ **Natural discovery**:
```python
# Does industry affect approval?
org_approval.groupby('industry_type')['got_approved'].mean()
# Next cell: "Tech 69%, E-commerce 45%. Big difference"
```

---

## Research-Guided Exploration (Don't Cite)

### Use Research to Guide Questions

**Research insight** → **Natural exploration**:
- Benchmarks show 17% median activation → Check: How does Mercury compare?
- Brex got +29% lift from industry personalization → Test: Do industries prefer different products?
- Churn benchmarks 25-40% for banking → Explore: When do orgs churn?

**DON'T cite research directly**:
```
❌ "Research shows median activation is 17%, so Mercury's 39% is above benchmark"
✅ "39.4% activation rate" → natural discovery that it's higher than typical
```

---

## Realistic Exploration Techniques

### 1. Show Dead Ends

```python
# Try to find first product adopted
product_first_active = products[products['is_active']==True].groupby(['organization_id', 'product'])['day'].min()
first_product = product_first_active.loc[product_first_active.groupby('organization_id').idxmin()]
first_product['product'].value_counts()
```
```markdown
Bank Account is first for almost everyone. Makes sense since they get it when approved.
```
```markdown
What about first NON-bank product?
```
```python
# Try again excluding Bank Account
non_bank_first = ...
# (This might not yield much)
```

### 2. Statistical Testing

```python
# Is the Credit Card difference significant?
from scipy.stats import chi2_contingency
tech_cc = cc_data[cc_data['industry_type'] == 'Technology']['is_active']
other_cc = cc_data[cc_data['industry_type'] != 'Technology']['is_active']
print(tech_cc.mean(), other_cc.mean())
```
```python
# Chi-square test
chi2, p = chi2_contingency([[tech_yes, tech_no], [other_yes, other_no]])[:2]
print(f'p-value: {p}')
```
```markdown
p < 0.001. Highly significant
```

### 3. Natural Pivots

```markdown
How long does activation take?
```
```python
# Get approval and activation dates
approved_dates = funnel[funnel['funnel_stage']=='approved'][['organization_id', 'date']]
# ... natural progression
```
```markdown
By industry?
```
```python
time_to_active.groupby('industry_type')['days'].median()
```
```markdown
Tech activates faster. 11 days vs 28 for E-commerce
```

---

## Cell Structure Examples

### ✅ Natural Cell Progression

```python
# Cell 1
orgs.head()
```
```python
# Cell 2
orgs.shape
```
```markdown
# Cell 3
500 orgs
```
```python
# Cell 4
orgs['industry_type'].value_counts()
```
```markdown
# Cell 5
3 main industry types
```

### ❌ Artificial Batching

```python
# Cell 1
print(f"Dataset shape: {orgs.shape}")
print(f"Industry types: {orgs['industry_type'].nunique()}")
print(f"Industry distribution:\n{orgs['industry_type'].value_counts()}")
```

---

## Language Guidelines

### Natural Observations
- "That's high" not "This indicates a high rate"
- "Big drop" not "Significant decrease"
- "Makes sense" not "This is logical because"
- "Interesting" not "It is noteworthy that"

### Simple Questions
- "Does industry matter?" not "Let me investigate whether industry affects outcomes"
- "How long to activate?" not "I will now analyze the time to activation"

### Direct Statements
- "79% churn" not "The churn rate is 79%"
- "Tech adopts more" not "Technology companies demonstrate higher adoption rates"

---

## Testing and Validation

### Before Adding to Notebook
Always test code first:
```bash
uv run python -c "import pandas as pd; orgs = pd.read_csv('orgs.csv'); print(orgs.shape)"
```

### Natural Error Handling
If something doesn't work, show it:
```python
# Try a quick model
model = LogisticRegression()
model.fit(X, y)
print(f'Accuracy: {model.score(X, y):.3f}')
```
```markdown
Basic model. Not great predictive power but confirms industry matters.
```

---

## Summary

**The goal is to make notebooks look like real work, not presentations.**

Key principles:
1. One thought per cell
2. Learn from output in next cell
3. Natural language observations
4. Show exploration dead ends
5. Simple calculations over complex print statements
6. Research guides questions, doesn't get cited
7. 5 hours of work should look like 5 hours, not 30 minutes

**Reference examples**:
- `matt_strautmann_GoFundMe_donor_ltv.ipynb` (natural style)
- `matt_strautmann_mercury_analysis.ipynb` (realistic 5-hour exploration)