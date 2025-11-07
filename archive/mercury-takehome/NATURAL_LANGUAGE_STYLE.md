# Natural Language Style Guide

## Learned from: matt_strautmann_GoFundMe_donor_ltv.ipynb

### Core Principle
**Write like you're typing notes to yourself during analysis, not presenting to an audience.**

Shortest natural phrasing. Drop unnecessary connector words.

---

## ✅ DO Use

### Direct Observations
```
"Found:"
"Learning:" or "Learnings:"
"Approval rate is 55.6%, only 39.4% reach activation. Pretty significant drop-off."
"Churn is really high:"
"Interesting - only 278 orgs have product data."
```

### Actions (present continuous)
```
"Looking at X next."
"Checking how long it takes orgs to activate."
"Digging deeper into product adoption."
"Joining orgs with funnel data."
```

### Questions (direct)
```
"# Do free events drive donations?"
"# Does Q4 timing matter?"
"# Which acquisition channel drives LTV?"
```

### Code Comments (minimal)
```
# Learning: AVG was skewed by $1 transactions
# Statistically insignificant difference
# Evaluate std of amount
# payments review
```

---

## ❌ DON'T Use

### Over-explaining
```
❌ "So approval rate is 55.6%, and only 39.4% reach activation. That's pretty significant."
✅ "Approval rate is 55.6%, only 39.4% reach activation. Pretty significant drop-off."
```

### Formal/Structured
```
❌ "What I found:"
✅ "Found:"

❌ "What I learned:"
✅ "Learning:"

❌ "Upon analyzing the data, I discovered..."
✅ "Found:"

❌ "The findings indicate that..."
✅ [Just state the finding directly]

❌ "It is interesting to note that..."
✅ "Interesting -"
```

### Unnecessary "Let me"
```
❌ "Let me check how long it takes orgs to activate."
✅ "Checking how long it takes orgs to activate."

❌ "Let me join orgs with funnel data."
✅ "Joining orgs with funnel data."

❌ "Let me look at which products..."
✅ "Looking at which products..."
```

### Connector Words to Drop
Drop: "So", "and" (when connecting sentences), "That's", "It is", "This is"

```
❌ "That matches exactly with the 278 approved orgs!"
✅ "Matches exactly with the 278 approved orgs."

❌ "It is concerning since that's the core product."
✅ "Concerning since it's the core product."
```

---

## Pattern Examples from Reference

### From GoFundMe notebook:
- "# Learning: AVG was skewed by a lot of $1 transactions:"
- "# Learnings: Free events are great for acquisition and lead to higher LTV on average."
- "# Statistically insignificant difference. Still business impact to consider."
- "# Do free events drive donations?"
- "# Which acquisition channel drives LTV?"
- "# Is it significant?"

### Good Mercury examples:
- "Found: 3 industry_types, 15 specific industries..."
- "Approval rate is 55.6%, only 39.4% reach activation. Pretty significant drop-off."
- "Interesting - only 278 orgs have product data. Matches exactly with the 278 approved orgs."
- "Churn is really high: Invoicing 100%, Bank Account 79%..."
- "Looking at funnel next."
- "Digging deeper into product adoption."

---

## Technical Formatting

### F-strings
```python
✅ f"Column: {df['column']}"       # Double outer, single inner
❌ f'Column: {df["column"]}'       # Escaped quotes look wrong
```

### Comments in Code
Keep minimal and direct:
```python
✅ # Check null dates
✅ # Learning: Most orgs are micro
✅ # Does growth potential matter?

❌ # Let me check the null dates
❌ # What I learned: Most orgs are micro
❌ # I want to see if growth potential matters
```
