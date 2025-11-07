# Mercury Analysis Summary - Key Findings for Experiences Team

*Written after completing exploratory analysis of 500 orgs, onboarding funnel, and product usage data*

## Core Questions Answered

### 1. Which industries have highest approval rates?

**Technology leads at 69%, E-commerce lowest at 45%**
- Technology: 69% (106/153 orgs approved)
- Consulting: 57% (71/124 orgs approved)
- E-commerce: 45% (101/223 orgs approved)

*Found in cells 29-30: Clear hierarchy, Technology performs 24 percentage points better than E-commerce*

### 2. Does growth potential affect product adoption?

**High-growth orgs adopt Credit Card 7x more frequently**
- High-growth: 14.4% Credit Card adoption
- Low-growth: 1.9% Credit Card adoption
- Effect extends across all non-Bank products

*Found in cells 45-46: Most dramatic difference is Credit Card (14% vs 2%), shows growth potential is strong predictor*

### 3. What does product churn look like?

**Churn is high across all products, Invoicing worst**
- Invoicing: 44% churn rate (7/16 users)
- Bank Account: 24% churn rate (42/173 users)
- Credit Card: 25% churn rate (5/20 users)
- Debit Card: 20% churn rate (27/136 users)

*Found in cells 51-52: Defined churn as >30 days inactive. Major retention issue across board*

## Key Additional Learnings

### Industry-Product Preferences Are Strong
- **Technology strongly prefers Credit Card**: 13% vs 3% for other industries
- **Statistical significance confirmed**: p=0.005 (cell 43)
- **Clear personalization opportunity**: Industry-specific featuring could work

### Activation Performance Context
- **39% activation rate**: Above industry median of 17%
- **Big funnel drop**: 56% approval → 39% activation (17 point drop)
- **Technology activates fastest**: 11 days vs 28 for E-commerce

### Product Usage Reality
- **Debit Card most active**: 17,120 active usage records vs 5,591 Bank Account
- **Invoicing barely used**: Only 48 active records total
- **Only approved orgs use products**: 278 unique product users = 278 approved orgs

## Experiment Recommendation

**High-confidence opportunity**: Industry-specific product recommendations during onboarding

**Evidence**: Clear preferences exist (13% vs 3% Credit Card for Tech), statistically significant, 20% lift achievable

**Sample size needed**: 717 approved orgs for 80% power, ~6 months runtime

---

# Dashboard Design: Mercury Onboarding Analytics

## Primary Use Cases

**For Experiences Product Team:**
- Monitor industry-specific funnel performance
- Identify product-market fit by segment
- Track experiment results and rollout decisions
- Deep-dive on churn and activation issues

**For Account Management:**
- Understand industry benchmarks for pipeline forecasting
- Identify at-risk segments early
- Tailor onboarding recommendations

## Dashboard Structure

### 1. Executive Overview Tab
**Top-line metrics with industry breakdowns:**
- Approval rate by industry_type (current: 56% overall)
- Activation rate by industry_type (current: 39% overall)
- Time-to-activation by industry (current: 18 days median)
- Product adoption rates (current: 52% adopt non-Bank products)

**Visual**: Side-by-side bar charts showing industry_type performance

### 2. Funnel Deep-Dive Tab
**Stage-by-stage conversion analysis:**
- Application → Approved → First Deposit → First Active
- Drop-off points highlighted (biggest: Approved → First Active)
- Time-in-stage distributions
- Industry/segment filtering

**Visual**: Sankey diagram showing flow through stages with drop-off sizing

### 3. Product Adoption Analysis Tab
**Product-specific insights:**
- Adoption rate by product × industry matrix
- Time-to-first-usage by product
- Multi-product adoption patterns (which products are adopted together)
- Growth potential impact on adoption

**Visual**: Heat map showing adoption rates, timeline charts for usage patterns

### 4. Churn & Retention Tab
**Product stickiness monitoring:**
- Churn rate by product over time
- Days-since-last-active distributions
- Cohort analysis (orgs approved in same month)
- Early warning indicators (usage dropping)

**Visual**: Retention curves by product, churn rate trend lines

### 5. Experiment Tracker Tab
**A/B test monitoring:**
- Real-time results for active experiments
- Confidence intervals and statistical significance
- Subgroup analysis (by industry, segment)
- Guardrail metrics monitoring

**Visual**: Forest plots showing treatment effects, control charts for guardrails

## Interactive Features

### Filters (Available on All Tabs)
- **Date range slider**: Last 30/90/365 days or custom
- **Industry type**: Technology, E-commerce, Consulting (multi-select)
- **Segment size**: Micro, Small, Medium
- **Growth potential**: High vs Low
- **Approval status**: All, Approved only, Activated only

### Drill-Down Capabilities
- Click any metric to see underlying org list
- Export filtered data for deeper analysis
- Save custom views and alerts
- Cohort comparison tool (compare time periods)

## Data Refresh & Alerts

### Automation
- **Daily refresh**: New org data, updated funnel stages
- **Weekly summary**: Email with key metric changes
- **Anomaly detection**: Alert if approval/activation rates drop >5%

### Self-Service Capabilities
- **Custom date ranges**: Ad-hoc analysis periods
- **Segment creation**: Define custom industry groupings
- **Export functionality**: CSV download for any filtered view
- **Report scheduling**: Automated weekly/monthly reports

## Technical Requirements

### Data Sources
- Organizations table (demographics)
- Adoption funnel stages (with timestamps)
- Product usage daily grain (activity flags)
- Experiment assignment tables (for A/B tests)

### Performance Needs
- **Sub-second load times** for standard views
- **Real-time updates** for experiment monitoring
- **Historical data access** back 2+ years for trends

### Access Control
- **Experiences team**: Full dashboard access
- **Account managers**: Read-only, filtered to their segments
- **Leadership**: Executive summary view only
- **Data team**: Admin access for configuration

## Success Metrics for Dashboard

**Adoption**: 80% of Experiences team uses weekly
**Self-service**: 50% reduction in ad-hoc analysis requests to data team
**Decision speed**: Product decisions made 2x faster with data evidence
**Experiment velocity**: 25% more experiments launched due to easier monitoring

---

*This dashboard would enable the Experiences team to identify opportunities like the Credit Card-Technology affinity we found, monitor experiment results in real-time, and make data-driven decisions about industry-specific product recommendations.*