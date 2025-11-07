# Onboarding Flows & Product Adoption: Research Document
## Context for Mercury Data Science Take-Home Analysis

**Author**: Matt Strautmann
**Date**: 2025-10-30
**Purpose**: Background research for designing industry-specific product recommendation experiment

---

## Table of Contents
1. [Part 1: Onboarding Flows & Product Adoption](#part-1-onboarding-flows--product-adoption)
2. [Part 2: A/B Test Experiment Design](#part-2-ab-test-experiment-design)
3. [Application to Mercury Take-Home](#application-to-mercury-take-home)

---

# Part 1: Onboarding Flows & Product Adoption

## 1.1 Onboarding Flow Best Practices (2024)

### Core Principles

**Primary Goal**: Get users to their activation moment as quickly and clearly as possible. A well-structured onboarding flow reduces time-to-value (TTV), which leads to increased user activation and long-term retention.

### Eight Critical Best Practices

#### 1. Minimize Friction
Reduce the number of steps in the customer journey to speed up time to value and prevent decision paralysis. Make your first impression as frictionless as possible.

**Why it matters**: Unnecessary steps create drop-off points. Each additional click or form field reduces completion rates.

#### 2. Personalize the Experience
Different user personas need different features, so they need different onboarding experiences. Tweak the onboarding flow to match the user's role or what they're trying to achieve.

**Impact**: Brex (B2B fintech) segmented users by industry and created tailored landing pages for each, leading to a **29% increase in completed card applications**.

#### 3. Use Interactive Elements
Let users get hands-on from the start by encouraging small actions so they're actively involved rather than passively reading. Create interactive walkthroughs that put users in active exploration mode.

#### 4. Implement Onboarding Checklists
Add structure to the journey by breaking it into bite-sized, manageable tasks. Introduce only the key **3-5 tasks** whose completion correlates with activation and product adoption.

**Key insight**: Don't overwhelm. Focus on tasks that directly lead to the "aha moment."

#### 5. Celebrate Progress
Celebrating small wins (like completing a key task) makes onboarding feel rewarding and motivates users.

#### 6. Measure Key Metrics
Track these onboarding metrics:
- **Activation rate**: % of new users who reach the key action that signals value realization (most telling metric)
- **Time-to-value (TTV)**: How long it takes users to reach activation milestone after signing up
- **Drop-off points**: Where confusion, friction, or fatigue cause abandonment

#### 7. Provide On-Demand Support
Resource centers with how-to guides, video tutorials, product documentation, and chatbots enable self-service support.

#### 8. Continuously Optimize
Use product analytics to track user activation rates, time to value, and feature adoption. Measure performance to understand what works and what doesn't.

---

## 1.2 Key Onboarding Metrics

### Activation Rate

**Definition**: The number of users who begin a product trial and reach a specific touchpoint or milestone (e.g., syncing with Google account, uploading a file, completing 2+ transactions).

**Formula**:
```
Activation Rate = (Users who reached activation milestone / Users who signed up) × 100
```

**Why it matters**: Highlights how effective your onboarding process is and whether users quickly experience the value your product promises. High activation typically leads to better retention and long-term engagement.

**Benchmarks**:
- Median SaaS activation rate: **17%**
- Top-performing SaaS companies: **65%**

### Time to Value (TTV)

**Definition**: The amount of time it takes for a user to experience the core value of your product after signing up.

**Related Concepts**:
- **Time to First Value (TTFV)**: How long until the first meaningful benefit (initial "wow" moment)
- **Time to Value (TTV)**: How long until full, long-term value realization

**Measurement**: Typically measured in user clicks or minutes.

**Why it matters**: The faster users understand the value and how it solves their problems, the more likely they'll keep returning to it.

---

## 1.3 Product Adoption Funnel

### Funnel Stages

A product adoption funnel tracks how users progress from discovering your product to becoming loyal advocates. Each stage represents a critical milestone:

1. **Awareness**: User discovers the product
2. **Onboarding**: User completes signup and initial setup
3. **Activation**: User reaches first value milestone
4. **Engagement**: User regularly interacts with core features
5. **Retention**: User continues using product over time
6. **Advocacy**: User recommends product to others

### Key Metrics by Stage

| Stage | Primary Metric | What It Measures |
|-------|---------------|------------------|
| Onboarding | Signup completion rate | % who finish signup process |
| Activation | Activation rate | % who reach activation event |
| Engagement | Feature adoption rate | % using key features |
| Retention | Retention rate | % still active after 30/60/90 days |
| Churn | Churn rate | % who stop using product |

**Feature Adoption Funnel**:
- **Exposed**: Users learn about features through onboarding
- **Activated**: Users enable or access new features
- **Used**: Users go beyond activation and use feature as intended

---

## 1.4 Retention & Churn Analysis

### Retention Focus

Retention is about keeping users engaged and satisfied over time by:
- Delivering ongoing value
- Addressing user needs and concerns
- Providing excellent customer support
- Proactively preventing churn

**Critical insight**: Many businesses focus too much on acquisition and ignore retention, even though **it's easier and cheaper to retain existing customers than acquire new ones**.

### Churn Funnel

The churn funnel (cancellation funnel) tracks the steps before users leave the product for good.

**Relationship to Adoption**: Higher adoption rates mean new users interact with more features, increasing the value they get and **reducing the likelihood of churn**.

### Benchmarks

- **Activation rates**: 17%–65% (median to top performers)
- **Churn rates** (top SaaS companies): 3%–5%

---

## 1.5 Industry-Specific Personalization

### The Case for Segmentation

**User frustration**: 74% of customers experience frustration when website content is not personalized.

**Approach**: Filter and group customers based on specific attributes and send contextual, personalized messages to each segment. This is particularly crucial for B2B SaaS since customers come from a wide range of industries, each with different motivations and goals.

### Benefits

1. **Improved Engagement**: Tailoring tutorials, in-app tips, or product recommendations to the user's specific needs delivers a more personalized and meaningful experience.

2. **Faster Activation**: Showcasing features most relevant to the user's goals helps users see immediate value, increasing motivation to explore and adopt the product further.

3. **Higher Conversion Rates**: Personalized onboarding can improve free-to-paid conversion rates.

### Real-World Example: Brex

**Company**: Brex (B2B financing for life sciences, ecommerce, and tech startups)

**Approach**: Segmented users by industry and created tailored landing pages for each industry segment.

**Result**: **29% increase in completed card applications**

### Implementation Strategy

Use segmentation to provide relevant recommendations based on:
- Preferences
- Past behaviors
- Browsing history
- Industry or vertical
- Company size or segment
- Growth potential

---

## 1.6 B2B Fintech Onboarding Context

### Market Overview (2024)

- **Fintech SaaS market**: Projected to hit **$949 billion by 2028**
- **B2B Fintech SaaS**: Leading in funding and growth
- **Critical problem**: 25-40% of new checking accounts close within the first year

### Customer Segmentation Challenges

Adjusting to different customer needs and platforms is a significant challenge for fintech companies during B2B onboarding. Companies must:
- Understand specific needs of each customer segment
- Tailor the platform to suit their preferences
- Address pain points in payments, accounting, and treasury management

### Growth Areas

Next wave of growth will come from:
- **B2B(2X)**: Business-to-business-to-consumer models
- **Financial infrastructure**: Embedded fintech in SaaS platforms
- **Lending**: Expanded credit products

---

# Part 2: A/B Test Experiment Design

## 2.1 Experiment Design Fundamentals

### Randomization Strategies

#### Simple Randomization
- Requires no historical information
- Can be applied to any users as they arrive
- Risk: Imbalance in influential factors, especially with small samples

#### Stratified Randomization
- Requires knowing the cohort in advance
- Needs access to relevant user data
- Prevents imbalance between treatment groups for known factors that influence outcomes

### When to Use Stratified Randomization

**Use stratified randomization when**:

1. **Small sample sizes**: Particularly important for trials with fewer than 400 units when stratification factors have a large effect on prognosis

2. **Known influential factors**: When certain factors are known to influence outcomes (e.g., industry, company size, growth potential)

3. **Group-level randomization**: When there aren't many units of randomization, stratification eliminates the possibility that all units of a certain type are assigned to one group

4. **Interim analyses planned**: Important for large trials when interim analyses are planned with small numbers of observations

**Benefits**:
- Reduces false positive rate
- Enforces balance between groups
- Increases statistical power when stratification variables correlate with the outcome

**Choosing stratification variables**:
- Pick factors that affect the outcome (age, location, usage frequency, industry, segment)
- Ideally use **4-6 strata** (more can cause variables to cancel out each other's impact)

---

## 2.2 Statistical Rigor

### Sample Size Calculation

Sample size depends on several factors:

| Factor | Description | Typical Value |
|--------|-------------|---------------|
| **Statistical Power** | Probability of detecting MDE if it exists | 0.8 (80%) |
| **Significance Level (α)** | False positive rate threshold | 0.05 (5%) |
| **Baseline Conversion Rate** | Current performance | Varies by metric |
| **Minimum Detectable Effect (MDE)** | Smallest meaningful improvement | Business-driven |

**Example**:
- Power: 0.8
- Reliability: 0.95 (one-sided test)
- Baseline: 4% conversion
- Expected: 5% conversion
- **Required sample size**: 5,313 per group

**Key insight**: MDE has a **dramatic effect** on required traffic to reach statistical significance. Smaller effects require much larger samples.

### Statistical vs. Practical Significance

#### Statistical Significance
**Question**: "Is this real?" (Did this happen by chance?)

**Measure**: p-value < 0.05 means <5% probability the observed difference was a fluke

**Limitation**: Can find "significant" results that don't matter in practice

#### Practical Significance
**Question**: "Does this matter?" (Is the impact meaningful?)

**Measure**: Effect size (e.g., percentage point change, time saved, revenue impact)

**Key consideration**: A statistically significant result with a tiny effect size might not justify implementation costs

#### Business Impact
**Question**: "Should we do this?" (Is it worth it?)

**Factors to consider**:
- Cost of implementation
- Feasibility and timeline
- Alignment with organizational values
- Opportunity cost vs. other initiatives

### The Three-Pillar Decision Framework

**Best practice**: Teams that focus solely on p-values tend to ship lots of tiny "improvements" that add up to nothing. Teams that balance all three metrics ship fewer changes, but each one actually moves the needle.

**Process**:
1. Set thresholds before running the test
2. Decide what effect size would make implementation worthwhile
3. Calculate minimum detectable effect (MDE)
4. Run test until statistical significance
5. Check effect size and confidence intervals
6. Evaluate business impact (cost, feasibility, alignment)

---

## 2.3 Guardrail Metrics

### Definition

Guardrail metrics monitor and control system behavior, ensuring operations stay within acceptable boundaries. Unlike primary success metrics that measure intended outcomes, they're your **early warning system**.

**Purpose**: A test can appear successful at first glance but have an unintended impact on other aspects of your product and user experience. Guardrail metrics give insight into the broader impact of an experiment.

### Types of Guardrails

1. **Trust-Related Guardrails**:
   - Sample Ratio Mismatch (most important)
   - Data quality checks

2. **Organizational Guardrails**:
   - User experience metrics (page load time, error rates)
   - Revenue/monetization metrics
   - Engagement metrics for other features

### Implementation Approaches

**Airbnb's Three Guardrails**:

1. **Impact Guardrail**: Requires that the global average treatment effect is not more negative than a preset threshold (protects against large negative effects regardless of statistical significance)

2. **Inferiority Test**: Try to prove that the treatment group does worse than control group

3. **Non-Inferiority Test**: Try to prove that the treatment group does better than a certain pre-defined margin relative to control

### Testing Methods

- **Inferiority test**: Try to prove treatment does worse than control
- **Non-inferiority test**: Try to prove treatment does better than a pre-defined margin relative to control

---

## 2.4 Heterogeneous Treatment Effects (HTE)

### Definition

**Heterogeneous Treatment Effect (HTE)** occurs when different sub-populations in an experiment respond to the same treatment in significantly different ways.

### Why It Matters

If one group responds to a change at a significantly different rate than another group, then average treatment effects will be **skewed towards the behavior of one group**, potentially hiding important differences.

**Connection to guardrails**: Unintended side-effects can often be caught by using guardrail metrics and automatically detecting heterogeneous treatment effects.

### Application

Use HTE analysis to:
- Detect differential impacts across user segments (by industry, segment, growth potential)
- Identify which groups benefit most from treatment
- Avoid "average effect" fallacy where treatment helps some but hurts others
- Inform selective rollout decisions

---

## 2.5 Analysis Methods

### Cohort Analysis

**Definition**: Comparison of survival analysis between two or more groups, where users are grouped by a common characteristic (e.g., signup month, industry, segment).

**Product adoption applications**:
- Track adoption of new products or features
- Compare retention across cohorts
- Identify which cohorts (segments) are having problems
- Learn how long customers stick around and when they're most likely to churn
- Understand time to value (how long for free users to convert to paid)

**Time-based cohorts**: In SaaS, compare survival curves between cohorts of times when users start using the service to see if the service is improving to retain users longer.

### Survival Analysis (Time-to-Event)

**Definition**: A branch of statistics for analyzing the expected duration of time until one event occurs (also known as time-to-event analysis).

**Applications for product teams**:
- Understand not only how customers retain or churn over time, but also **when** they're most likely to churn
- Measure time to product adoption (how long until users activate a feature)
- Analyze feature adoption patterns over time
- Identify critical time windows for intervention

**Combined with cohort analysis**: Provides powerful insights into user retention, product stickiness, and feature adoption patterns over time.

### Subgroup Analysis

Break down results by:
- Industry type or specific industry
- Company segment (size × growth potential)
- User role or persona
- Acquisition channel
- Prior behavior patterns

**Goal**: Identify heterogeneous treatment effects and inform selective rollout strategies.

---

## 2.6 Experiment Decision Framework

### Result → Action Mapping

Define decision thresholds **before** running the experiment:

| Result Category | Statistical Sig. | Effect Size | Business Impact | Action |
|----------------|------------------|-------------|-----------------|--------|
| **Strong Positive** | p < 0.05 | > MDE threshold | High ROI | Full rollout to all users |
| **Moderate Positive** | p < 0.05 | > MDE threshold | Positive for some segments | Selective rollout by segment |
| **Weak Positive** | p < 0.05 | < MDE threshold | Low ROI | Do not implement (not worth cost) |
| **Neutral** | p ≥ 0.05 | N/A | N/A | Iterate on design or abandon |
| **Negative** | p < 0.05 | Effect is negative | Harmful | Abandon immediately |

### Define Success Thresholds

**Strong positive thresholds** (examples):
- +10% relative lift in activation rate
- -20% reduction in time to first product adoption
- +15% increase in multi-product adoption rate
- +5 percentage points absolute lift in feature usage

**Guardrail thresholds** (do not violate):
- No decrease in approval rates
- No increase in early-stage drop-off
- No degradation in time to approval or first deposit

### Plan for Unexpected Results

**Scenario 1: Works for some industries, hurts others** (HTE detected)
- Action: Selective rollout only to industries showing positive effects
- Further investigation: Why did it hurt certain industries?

**Scenario 2: Strong positive on secondary metric, neutral on primary**
- Action: Evaluate if secondary metric is valuable enough to justify
- Consider: Longer test duration to detect smaller effects on primary metric

**Scenario 3: Guardrail metric violated despite positive primary metric**
- Action: Do not roll out
- Investigation: Understand and fix unintended harm before retrying

### Early Stopping Criteria

**Success criteria** (stop early and roll out):
- Statistical significance achieved on primary metric
- Practical significance threshold met
- All guardrail metrics passing
- Consistent positive effect across key segments

**Futility criteria** (stop early and abandon):
- Very unlikely to reach statistical significance given trajectory
- Negative trend on primary metric
- Guardrail violations detected
- Implementation complexity not justified by modest effects

---

# Part 3: Application to Mercury Take-Home

## 3.1 Problem Space

**Context**: Mercury is a B2B banking platform for startups. The Experiences team wants to feature products for different industries during onboarding to drive earlier product adoption.

**Current Proposal**: Vary featured product depending on `industry_type` or `industry` of the organization.

## 3.2 Key Questions to Answer with Data

### Part 1: Exploratory Analysis

Using onboarding flow and product adoption frameworks:

1. **Industry × Approval Rates**
   - Which industries/industry_types have highest approval rates?
   - Sample size considerations (statistical significance)

2. **Segment × Product Adoption**
   - Does growth potential affect likelihood to adopt different products?
   - Which segments adopt Credit Card vs Invoicing vs Debit Card?
   - Time to adoption by segment

3. **Product Churn Analysis**
   - Define churn: was active → became inactive for 30+ days
   - Churn rate by product, industry, segment
   - When are users most likely to churn? (cohort analysis)

4. **Activation Metrics**
   - What % of approved orgs reach `first_active` status?
   - Time to first deposit, time to first active
   - Drop-off points in adoption funnel

### Part 2: Experiment Design

Using A/B testing framework:

1. **Segmentation Strategy** (industry_type vs industry)
   - Which has stronger product preference signals?
   - Sample size per segment
   - Stratification approach

2. **Treatment Design**
   - Which product to feature for which industry/segment?
   - Control: current onboarding (no featured product)
   - Treatment: featured product based on industry

3. **Statistical Design**
   - Primary metric: time to product adoption? adoption rate? activation rate?
   - MDE: What lift justifies implementation?
   - Sample size calculation
   - Expected runtime (given org volume)
   - Stratification variables: segment_size? segment_growth_potential? industry_type?

4. **Guardrail Metrics**
   - Approval rate (ensure no decrease)
   - Time to first deposit (ensure no delay)
   - Time to activation (ensure no delay)
   - Adoption of other products (ensure no cannibalization)

5. **HTE Analysis**
   - By industry_type or industry
   - By segment (size × growth potential)
   - Identify which segments benefit most

6. **Decision Framework**
   - Strong positive: +X% adoption rate → full rollout
   - Positive for some industries: selective rollout
   - Neutral: iterate or abandon
   - Negative or guardrail violation: abandon

## 3.3 Recommended Analysis Approach

### Phase 1: Understand Current State

1. **Funnel conversion rates**: application → approved → first_deposit → first_active
2. **Product adoption patterns**: Which products do orgs adopt? In what order? How quickly?
3. **Industry/segment differences**: Do patterns vary by industry_type, industry, or segment?

### Phase 2: Identify Product-Industry Affinities

1. **Product adoption rate by industry**: E-commerce → Invoicing? Consulting → Debit Card?
2. **Time to adoption by industry**: Which industries adopt which products fastest?
3. **Multi-product adoption**: Which industries adopt multiple products?

### Phase 3: Design Experiment

1. **Choose segmentation**: industry_type vs industry (based on sample sizes and signal strength)
2. **Define treatment**: Which product to feature for each segment
3. **Calculate sample size**: Based on baseline adoption rates and desired MDE
4. **Set up stratification**: If needed (likely by segment or large industry_type groups)
5. **Define guardrails**: Ensure no harm to approval, activation, or other products

### Phase 4: Analysis Plan

1. **Primary analysis**: Two-sample test (t-test or chi-square) on adoption rate or time-to-adoption
2. **Subgroup analysis**: By industry, segment, growth potential (HTE detection)
3. **Guardrail checks**: Verify all secondary metrics are not harmed
4. **Cohort analysis**: Time-based patterns of adoption (survival curves)
5. **Decision**: Map results to action using pre-defined framework

---

## References & Benchmarks Summary

### Onboarding Metrics Benchmarks
- Median SaaS activation rate: **17%**
- Top-performing SaaS activation rate: **65%**
- Top SaaS churn rates: **3-5%**
- Financial services new account closure: **25-40%** in first year

### Personalization Impact
- Brex industry-specific onboarding: **+29%** completed applications
- Customer frustration without personalization: **74%**

### Statistical Testing
- Typical power: **0.8** (80%)
- Typical significance level: **0.05** (5%)
- Recommended stratification factors: **4-6 strata**

### Market Context (2024)
- Fintech SaaS market by 2028: **$949 billion**
- Growth areas: B2B(2X), financial infrastructure, embedded fintech

---

## Key Takeaways for Mercury Analysis

1. **Personalization works**: Industry-specific onboarding can drive significant lift (29% in Brex case)

2. **Balance three factors**: Statistical significance + Practical significance + Business impact

3. **Protect against harm**: Use guardrail metrics to ensure no unintended negative effects

4. **Expect variation**: HTE analysis will likely show some industries benefit more than others

5. **Start with data**: Let exploration guide experiment design (don't pre-plan based on assumptions)

6. **Activation is key**: Focus on metrics that correlate with retention (first_active, multi-product adoption)

7. **Consider stratification**: If sample sizes are small or segments differ significantly, stratify randomization

8. **Plan for selective rollout**: Be ready for scenario where treatment works for some industries but not others
