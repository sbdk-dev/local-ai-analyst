# Semantic Layer Design Notes

**Following**: Rasmus Engelbrecht's product analytics patterns
**Date**: 2025-11-05
**Phase**: 2 - Semantic Layer Setup

---

## Data Model: Product Analytics Lifecycle

### Why Product Analytics?

**Advantages over E-commerce**:
- Richer event-based data (not just transactions)
- Natural time-series patterns (DAU/MAU, retention, churn)
- Multiple analysis dimensions (users, features, cohorts, time)
- Common business questions map to semantic layer concepts
- Mirrors SaaS/product company analytics needs

**Rasmus Pattern**: Focus on user lifecycle, engagement, and feature adoption

---

## Core Entities

### 1. Users (Dimension Table)
**Purpose**: Customer demographic and signup information

**Dimensions**:
- `user_id` (PK)
- `signup_date` - When user signed up
- `plan_type` - free, starter, pro, enterprise
- `industry` - Customer industry vertical
- `company_size` - small, medium, large
- `country` - Geographic dimension

**Measures** (computed):
- `total_users` - COUNT(DISTINCT user_id)
- `users_by_cohort` - GROUP BY signup_month
- `plan_distribution` - COUNT by plan_type

### 2. Events (Fact Table)
**Purpose**: User actions and feature usage

**Dimensions**:
- `event_id` (PK)
- `user_id` (FK)
- `event_timestamp` - When action occurred
- `event_type` - login, feature_use, export, share, etc.
- `feature_name` - Which feature was used
- `session_id` - Session grouping

**Measures**:
- `total_events` - COUNT(*)
- `unique_users` - COUNT(DISTINCT user_id)
- `events_per_user` - COUNT(*) / COUNT(DISTINCT user_id)
- `avg_events_per_session` - GROUP BY session_id

### 3. Sessions (Aggregated from Events)
**Purpose**: User engagement sessions

**Dimensions**:
- `session_id` (PK)
- `user_id` (FK)
- `session_start` - First event timestamp
- `session_end` - Last event timestamp
- `session_date` - Date of session (for time-series)

**Measures**:
- `session_duration` - AVG(session_end - session_start)
- `sessions_per_user` - COUNT(session_id) / COUNT(DISTINCT user_id)
- `avg_events_per_session` - Total events / Total sessions

---

## Key Metrics (Following Rasmus)

### Engagement Metrics

**DAU (Daily Active Users)**:
```yaml
measure:
  name: dau
  type: count_distinct
  dimension: user_id
  filters:
    - event_timestamp >= CURRENT_DATE
    - event_timestamp < CURRENT_DATE + 1
```

**MAU (Monthly Active Users)**:
```yaml
measure:
  name: mau
  type: count_distinct
  dimension: user_id
  filters:
    - event_timestamp >= DATE_TRUNC('month', CURRENT_DATE)
```

**Stickiness (DAU/MAU ratio)**:
```yaml
measure:
  name: stickiness
  type: ratio
  numerator: dau
  denominator: mau
  description: "Measures how frequently users engage (higher = better)"
```

### Retention Metrics

**D1 Retention**:
```yaml
measure:
  name: d1_retention
  type: ratio
  numerator: users_active_day_1
  denominator: users_signed_up_day_0
  description: "% of users who return the day after signup"
```

**D7 Retention**, **D30 Retention**: Similar patterns

### Adoption Metrics

**Feature Adoption Rate**:
```yaml
measure:
  name: feature_adoption_rate
  type: ratio
  numerator: users_who_used_feature
  denominator: total_active_users
  dimension: feature_name
```

**Time to First Value (TTFV)**:
```yaml
measure:
  name: ttfv_median_days
  type: median
  dimension: days_to_first_key_action
  description: "Median days from signup to first valuable action"
```

---

## Sample Data Structure

### users.csv (1,000 users)
```csv
user_id,signup_date,plan_type,industry,company_size,country
user_001,2024-01-15,free,saas,small,US
user_002,2024-01-18,starter,ecommerce,medium,UK
user_003,2024-01-20,pro,fintech,large,US
...
```

### events.csv (50,000 events)
```csv
event_id,user_id,event_timestamp,event_type,feature_name,session_id
evt_001,user_001,2024-01-15 10:30:00,signup,account_creation,sess_001
evt_002,user_001,2024-01-15 10:35:00,feature_use,dashboard_view,sess_001
evt_003,user_001,2024-01-15 10:40:00,feature_use,report_export,sess_001
...
```

### sessions.csv (10,000 sessions, aggregated from events)
```csv
session_id,user_id,session_start,session_end,session_date,event_count
sess_001,user_001,2024-01-15 10:30:00,2024-01-15 10:45:00,2024-01-15,5
sess_002,user_001,2024-01-16 14:20:00,2024-01-16 14:35:00,2024-01-16,3
...
```

---

## Semantic Models (YAML Specs)

### Model 1: Users
**File**: `models/users.yml`

```yaml
model:
  name: users
  description: "User demographics and signup information"

dimensions:
  - name: user_id
    type: string
    primary_key: true

  - name: signup_date
    type: date
    description: "When user created account"

  - name: plan_type
    type: string
    description: "Subscription tier (free, starter, pro, enterprise)"

  - name: industry
    type: string
    description: "Customer industry vertical"

  - name: company_size
    type: string
    description: "Organization size (small, medium, large)"

measures:
  - name: total_users
    type: count_distinct
    dimension: user_id
    description: "Total unique users"

  - name: free_users
    type: count_distinct
    dimension: user_id
    filters:
      - plan_type = 'free'

  - name: paid_users
    type: count_distinct
    dimension: user_id
    filters:
      - plan_type != 'free'
```

### Model 2: Events
**File**: `models/events.yml`

```yaml
model:
  name: events
  description: "User actions and feature usage events"

dimensions:
  - name: event_id
    type: string
    primary_key: true

  - name: user_id
    type: string
    foreign_key: users.user_id

  - name: event_timestamp
    type: timestamp
    description: "When event occurred"

  - name: event_type
    type: string
    description: "Type of event (login, feature_use, export, etc.)"

  - name: feature_name
    type: string
    description: "Feature that was used"

measures:
  - name: total_events
    type: count
    description: "Total number of events"

  - name: unique_users
    type: count_distinct
    dimension: user_id
    description: "Unique users who triggered events"

  - name: events_per_user
    type: ratio
    numerator: total_events
    denominator: unique_users
```

### Model 3: Engagement
**File**: `models/engagement.yml`

```yaml
model:
  name: engagement
  description: "User engagement metrics (DAU/MAU, retention, stickiness)"

dimensions:
  - name: metric_date
    type: date
    description: "Date for time-series metrics"

  - name: cohort_month
    type: string
    description: "Signup month cohort (YYYY-MM)"

measures:
  - name: dau
    type: count_distinct
    dimension: user_id
    description: "Daily Active Users"
    time_window: 1 day

  - name: mau
    type: count_distinct
    dimension: user_id
    description: "Monthly Active Users"
    time_window: 30 days

  - name: stickiness
    type: ratio
    numerator: dau
    denominator: mau
    description: "DAU/MAU ratio (engagement frequency)"

  - name: d1_retention
    type: retention
    cohort_dimension: signup_date
    return_window: 1 day

  - name: d7_retention
    type: retention
    cohort_dimension: signup_date
    return_window: 7 days
```

---

## Example Business Questions → Queries

### Question 1: "What's our DAU trend this month?"
```python
# Via semantic layer
query_model(
    model='engagement',
    dimensions=['metric_date'],
    measures=['dau'],
    filters={'metric_date': 'last 30 days'}
)

# Generates SQL:
SELECT
  DATE(event_timestamp) as metric_date,
  COUNT(DISTINCT user_id) as dau
FROM events
WHERE event_timestamp >= CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY DATE(event_timestamp)
ORDER BY metric_date
```

### Question 2: "Which features do enterprise customers use most?"
```python
query_model(
    model='events',
    dimensions=['feature_name'],
    measures=['unique_users', 'total_events'],
    filters={'plan_type': 'enterprise'}
)
```

### Question 3: "What's our retention by industry?"
```python
query_model(
    model='engagement',
    dimensions=['industry', 'cohort_month'],
    measures=['d7_retention', 'd30_retention']
)
```

---

## Statistical Patterns to Apply

### From Mercury Learnings:

**1. Auto Sample Size Validation**:
```python
# When showing industry breakdown
if sample_size < 30:
    warning = "⚠️ Small sample size (n={n}). Results may be unstable."
```

**2. Auto Significance Testing**:
```python
# When comparing DAU across plan types
result = query_model('engagement', ['plan_type'], ['dau'])
chi_square_test = auto_test(result)  # Automatically run
interpretation = f"Pro users 2.3x higher DAU (p={p_value}, n={sample_sizes})"
```

**3. Effect Size Reporting**:
```python
# Always include practical significance
"D7 retention: Free 15% vs Pro 45% (30pp difference, p<0.001, n=450 vs n=120)"
```

---

## Next Steps

1. **Generate Sample Data** - Create realistic product analytics dataset
2. **Load to DuckDB** - `analytics.duckdb`
3. **Define Models** - Create 3 YAML semantic models
4. **Test Queries** - Validate via Ibis locally
5. **Document** - Capture design decisions

---

## References

- Rasmus's semantic layer guides (product analytics examples)
- Mercury project learnings (statistical rigor patterns)
- SaaS metrics playbook (DAU/MAU, retention, cohorts)

**Design Philosophy**:
- Start with business questions
- Metrics should be self-contained
- Dimensions enable slicing
- Simple and composable
