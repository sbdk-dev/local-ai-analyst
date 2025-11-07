# Semantic Model Documentation

**Project**: Claude Analyst AI System
**Phase**: 2 - Semantic Layer Setup
**Date**: 2025-11-05
**Status**: ✅ Complete

---

## Design Decisions

### 1. Data Model Choice: Product Analytics

**Decision**: Use product analytics lifecycle data (users → events → sessions) instead of e-commerce transactional data.

**Rationale**:
- **Richer event-based patterns**: Product analytics provides event streams, not just transactions
- **Natural time-series metrics**: DAU/MAU, retention curves, engagement stickiness
- **Multiple analysis dimensions**: Users × features × cohorts × time
- **Rasmus Engelbrecht patterns**: Following proven semantic layer design from Rasmus's guides
- **SaaS business relevance**: Mirrors real-world analytics needs for product companies

**Reference**: [DESIGN_NOTES.md](DESIGN_NOTES.md) lines 10-21

---

## Data Model Structure

### Core Entities

#### 1. Users (Dimension Table)
**Purpose**: Customer demographic and signup information

**Schema**:
```sql
CREATE TABLE users (
    user_id VARCHAR PRIMARY KEY,
    signup_date DATE,
    plan_type VARCHAR,  -- free, starter, pro, enterprise
    industry VARCHAR,   -- saas, ecommerce, fintech, healthtech, edtech, marketing, consulting
    company_size VARCHAR,  -- small, medium, large
    country VARCHAR
)
```

**Sample Size**: 1,000 users
**Plan Distribution**:
- Free: 596 (59.6%)
- Starter: 254 (25.4%)
- Pro: 116 (11.6%)
- Enterprise: 34 (3.4%)

**Industry Distribution**:
- SaaS: 268 (26.8%)
- E-commerce: 187 (18.7%)
- Fintech: 135 (13.5%)
- Healthtech: 119 (11.9%)
- Marketing: 110 (11.0%)
- Edtech: 98 (9.8%)
- Consulting: 83 (8.3%)

**Semantic Model**: [models/users.yml](models/users.yml)

---

#### 2. Events (Fact Table)
**Purpose**: User actions, feature usage, behavioral events

**Schema**:
```sql
CREATE TABLE events (
    event_id VARCHAR PRIMARY KEY,
    user_id VARCHAR,  -- FK to users
    session_id VARCHAR,
    event_timestamp TIMESTAMP,
    event_type VARCHAR,  -- signup, login, feature_use, logout
    feature_name VARCHAR  -- dashboard_view, report_create, api_call, etc.
)
```

**Sample Size**: 34,348 events across 2024
**Date Range**: 2024-01-03 to 2024-12-31

**Event Type Distribution**:
- feature_use: 25,194 (73.3%)
- login: 6,040 (17.6%)
- logout: 2,114 (6.2%)
- signup: 1,000 (2.9%)

**Top Features (by usage)**:
1. integration_setup: 2,626 uses (741 unique users)
2. dashboard_view: 2,596 uses (733 unique users)
3. api_call: 2,576 uses (746 unique users)
4. collaboration_edit: 2,559 uses (729 unique users)
5. report_export: 2,553 uses (725 unique users)

**Key Metrics**:
- 34.3 events per user (avg)
- 4.9 events per session (avg)
- 1,000 unique users generated events

**Semantic Model**: [models/events.yml](models/events.yml)

---

#### 3. Sessions (Derived Table)
**Purpose**: User engagement sessions (derived from events)

**Schema**:
```sql
CREATE TABLE sessions (
    session_id VARCHAR PRIMARY KEY,
    user_id VARCHAR,  -- FK to users
    session_start TIMESTAMP,
    session_end TIMESTAMP,
    session_date DATE
)
```

**Sample Size**: 7,055 sessions

**Session Metrics**:
- Average duration: 20.2 minutes
- Median duration: 12.0 minutes
- 7.1 sessions per user

**Semantic Model**: Referenced in [models/engagement.yml](models/engagement.yml)

---

## Semantic Models

### Model 1: Users (`users.yml`)

**Dimensions**:
- `user_id` (primary key)
- `signup_date`
- `plan_type` (free, starter, pro, enterprise)
- `industry` (7 verticals)
- `company_size` (small, medium, large)
- `country`

**Measures**:
- `total_users`: COUNT(DISTINCT user_id)
- `free_users`: COUNT(DISTINCT CASE WHEN plan_type = 'free')
- `paid_users`: COUNT(DISTINCT CASE WHEN plan_type != 'free')
- `conversion_rate`: paid_users / total_users
- `avg_tenure_days`: AVG(CURRENT_DATE - signup_date)

**Relationships**:
- → events (one_to_many)
- → sessions (one_to_many)

**Test Results**:
- ✅ 40.4% conversion rate (404 paid / 1,000 total)
- ✅ Plan distribution validated
- ✅ Industry distribution validated

---

### Model 2: Events (`events.yml`)

**Dimensions**:
- `event_id` (primary key)
- `user_id` (FK → users)
- `event_timestamp`
- `event_date` (derived: DATE(event_timestamp))
- `event_hour` (derived: EXTRACT(HOUR))
- `event_day_of_week` (derived: EXTRACT(DOW))
- `event_type` (signup, login, feature_use, logout)
- `feature_name` (10 features)
- `session_id`

**Measures**:
- `total_events`: COUNT(*)
- `unique_users`: COUNT(DISTINCT user_id)
- `events_per_user`: total_events / unique_users
- `feature_usage_count`: COUNT(CASE WHEN event_type = 'feature_use')
- `login_count`: COUNT(CASE WHEN event_type = 'login')
- `unique_sessions`: COUNT(DISTINCT session_id)
- `events_per_session`: total_events / unique_sessions

**Relationships**:
- → users (many_to_one)
- → sessions (many_to_one)

**Test Results**:
- ✅ 34.3 events/user
- ✅ 4.9 events/session
- ✅ Feature usage breakdown validated
- ✅ Cross-dimensional queries working (plan × events)

---

### Model 3: Engagement (`engagement.yml`)

**Type**: Derived model (joins users + events + sessions)

**Dimensions**:
- `metric_date` (for time-series)
- `cohort_month` (derived: TO_CHAR(signup_date, 'YYYY-MM'))
- `plan_type` (from users)
- `industry` (from users)

**Engagement Measures**:
- `dau`: Daily Active Users (users with events in last 24h)
- `wau`: Weekly Active Users (last 7 days)
- `mau`: Monthly Active Users (last 30 days)
- `stickiness`: DAU/MAU ratio (engagement frequency)
- `weekly_stickiness`: DAU/WAU ratio

**Session Measures**:
- `avg_session_duration_minutes`: AVG(session_end - session_start) / 60
- `avg_sessions_per_user`: sessions / unique users
- `avg_events_per_session`: events / sessions

**Feature Adoption**:
- `feature_adoption_rate`: users with feature_use / total users
- `power_users`: users with 10+ events in last 7 days

**Retention Measures**:
- `d1_retention`: % of users who return day 1 after signup
- `d7_retention`: % of users who return day 7 after signup
- `d30_retention`: % of users who return day 30 after signup

**Time to Value (TTV)**:
- `median_time_to_first_feature_minutes`: Median time from signup to first feature use
- `median_time_to_activation_days`: Median days to 5+ events (activation threshold)

**Test Results** (reference date: 2024-12-31):
- ✅ DAU: 77 users
- ✅ MAU: 628 users
- ✅ Stickiness: 12.3% (DAU/MAU)
- ✅ D1 Retention: 8.1%
- ✅ D7 Retention: 5.2%

---

## Key Findings from Testing

### 1. Plan Type Strongly Correlates with Engagement

**Test Query**: Plan type × average events per user

**Results**:
| Plan Type  | Avg Events/User |
|------------|-----------------|
| Enterprise | 156.1           |
| Pro        | 85.2            |
| Starter    | 43.3            |
| Free       | 13.7            |

**Insight**: Enterprise users are **11.4x more engaged** than free users. Clear progression across tiers.

**Implication**: Plan type is a strong predictor of product usage. Upgrade campaigns should focus on engagement metrics.

---

### 2. Industry-Specific Feature Preferences

**Test Query**: Top feature by industry

**Results**:
| Industry   | Top Feature        | Usage Count |
|------------|--------------------|-------------|
| SaaS       | collaboration_edit | 697         |
| E-commerce | collaboration_edit | 503         |
| Fintech    | dashboard_view     | 331         |
| Healthtech | team_invite        | 340         |
| Marketing  | team_invite        | 348         |

**Insight**: Industry preferences differ significantly. Team-oriented industries (SaaS, E-commerce) prefer collaboration features. Data-driven industries (Fintech) prefer dashboards.

**Implication**: Supports industry-specific onboarding recommendations (Mercury experiment design).

---

### 3. Retention Drops Significantly After D1

**Test Query**: D1 vs D7 retention

**Results**:
- D1 Retention: 8.1% (81/1,000 users)
- D7 Retention: 5.2% (52/1,000 users)

**Insight**: 36% drop from D1 to D7. Users who don't engage early are unlikely to return.

**Implication**: Critical to drive engagement in first 7 days. Onboarding interventions should focus on D1-D7 window.

---

### 4. Session Duration Distribution

**Results**:
- Average: 20.2 minutes
- Median: 12.0 minutes
- Difference: 8.2 minutes

**Insight**: Right-skewed distribution. Most sessions are short (~12 min), but some power users have much longer sessions (pushing average to 20 min).

**Implication**: Two distinct user segments: casual browsers (median) and power users (driving average up).

---

## Validation Results

### Database Connectivity
- ✅ DuckDB connection successful
- ✅ All 3 tables accessible via Ibis
- ✅ Indexes performing well

### Semantic Model Queries
- ✅ Basic measures (COUNT, COUNT DISTINCT, AVG)
- ✅ Derived dimensions (event_date, cohort_month)
- ✅ Time-based filters (DAU, WAU, MAU)
- ✅ Retention calculations (D1, D7)
- ✅ Cross-dimensional analysis (plan × events, industry × features)

### Data Quality
- ✅ No null values in primary keys
- ✅ All foreign keys valid
- ✅ Date ranges consistent (2024-01-03 to 2024-12-31)
- ✅ Event distributions realistic

---

## Implementation Learnings

### 1. Ibis Time Calculations
**Challenge**: Initial approach to calculate session duration failed:
```python
# ❌ This doesn't work:
duration_minutes = (_.session_end - _.session_start).seconds() / 60
```

**Solution**: Use pandas after fetching data:
```python
# ✅ This works:
sessions_df = sessions.execute()
sessions_df['duration_minutes'] = (sessions_df['session_end'] - sessions_df['session_start']).dt.total_seconds() / 60
```

**Learning**: Ibis interval columns don't have `.seconds()` method. For complex time calculations, fetch to pandas first.

---

### 2. Retention Calculations Require Joins
**Pattern**:
```python
user_events = (
    users
    .join(events, users.user_id == events.user_id)
    .mutate(days_since_signup=(_.event_timestamp.date() - _.signup_date).days)
)

d1_retention = (
    user_events
    .filter((_.days_since_signup >= 1) & (_.days_since_signup < 2))
    .aggregate(users_returned=_.user_id.nunique())
)
```

**Learning**: Cohort retention requires user-event joins with calculated day offsets. This pattern works cleanly in Ibis.

---

### 3. Realistic Data Distribution Matters
**Observation**: Generated data closely matches real-world patterns:
- Plan distribution: 60% free, 25% starter, 12% pro, 3% enterprise (realistic SaaS funnel)
- Event distribution: 73% feature_use, 18% login, 6% logout, 3% signup (natural activity)
- Session duration: Median 12 min, average 20 min (shows power user skew)

**Learning**: Realistic sample data validates semantic model patterns more effectively than uniform distributions.

---

## Next Steps (Phase 3)

### MCP Server Implementation
1. **FastMCP Setup**: Create MCP server with Claude Desktop integration
2. **Tool Design**:
   - `query_model(model, dimensions, measures, filters)` - Execute semantic layer queries
   - `explain_model(model)` - Show available dimensions/measures
   - `list_models()` - Show all semantic models
3. **Natural Language Interface**: Map user questions → semantic layer queries
4. **Statistical Rigor**: Auto-run significance tests, effect sizes, confidence intervals

### Intelligence Layer
1. **Incremental Query Builder**: One question per turn, each result informs next query
2. **Auto Statistical Testing**: Chi-square, t-tests when comparing groups
3. **Natural Language Generator**: Concise observations ("Tech 2x higher" not "Upon analyzing...")
4. **Fabrication Prevention**: Build → Execute → Annotate enforcement

---

## Files Created

### Semantic Models
- [models/users.yml](models/users.yml) - Users demographic model
- [models/events.yml](models/events.yml) - Events/feature usage model
- [models/engagement.yml](models/engagement.yml) - Engagement metrics model

### Data Files
- `data/users.csv` (1,000 rows)
- `data/events.csv` (34,348 rows)
- `data/sessions.csv` (7,055 rows)
- `data/analytics.duckdb` (9.5 MB)

### Scripts
- [generate_sample_data.py](generate_sample_data.py) - Data generation script
- [load_to_duckdb.py](load_to_duckdb.py) - DuckDB loader
- [test_queries.py](test_queries.py) - Semantic layer validation

### Documentation
- [DESIGN_NOTES.md](DESIGN_NOTES.md) - Initial design decisions
- [docs/FABRICATION_PREVENTION.md](docs/FABRICATION_PREVENTION.md) - Core pattern from Mercury project
- [docs/STATISTICAL_PATTERNS.md](docs/STATISTICAL_PATTERNS.md) - Auto statistical testing patterns
- [README.md](README.md) - Semantic layer quick start guide

---

## Success Criteria

**Phase 2 Complete**: ✅

- [x] Sample data generated (product analytics lifecycle)
- [x] Data loaded to DuckDB with indexes
- [x] 3 semantic models defined (users, events, engagement)
- [x] Queries validated via Ibis
- [x] Cross-dimensional analysis working
- [x] Engagement metrics calculated (DAU/MAU/stickiness)
- [x] Retention metrics working (D1/D7)
- [x] Design decisions documented

**Ready for Phase 3**: MCP Server Implementation

---

**Last Updated**: 2025-11-05
**Status**: Phase 2 Complete ✅
**Next Phase**: MCP Server + Intelligence Layer
