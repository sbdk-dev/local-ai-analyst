# Runtime Metrics - User Guide

## Overview

Runtime Metrics allow you to define custom metrics at runtime without editing YAML configuration files. This enables ad-hoc analysis and rapid iteration on metric definitions.

## Features

- **Define metrics at runtime** - No code changes required
- **Validate against semantic models** - Ensures dimension/measure compatibility
- **Persist to disk** - Metrics survive server restarts
- **Thread-safe** - Safe for concurrent access
- **Rich filtering** - Filter by model, tags, or name

## Metric Types

### 1. Count
Count total rows (no dimension needed).

```python
define_custom_metric(
    name="total_events",
    type="count",
    model="events",
    description="Total number of events"
)
```

### 2. Count Distinct
Count unique values of a dimension.

```python
define_custom_metric(
    name="power_users",
    type="count_distinct",
    model="users",
    dimension="user_id",
    filters={"login_count__gt": 100},
    description="Users with 100+ logins",
    tags=["engagement", "core"]
)
```

### 3. Sum
Sum values of a dimension.

```python
define_custom_metric(
    name="total_revenue",
    type="sum",
    model="users",
    dimension="revenue",
    description="Total revenue across all users"
)
```

### 4. Average
Average values of a dimension.

```python
define_custom_metric(
    name="avg_session_duration",
    type="avg",
    model="events",
    dimension="duration_seconds",
    filters={"event_type": "session"},
    description="Average session duration"
)
```

### 5. Ratio
Ratio of two metrics (numerator / denominator).

```python
define_custom_metric(
    name="conversion_rate",
    type="ratio",
    model="users",
    numerator="paid_users",
    denominator="total_users",
    description="Free to paid conversion rate"
)
```

### 6. Custom SQL
Custom SQL expression for advanced calculations.

```python
define_custom_metric(
    name="avg_revenue_per_user",
    type="custom_sql",
    model="users",
    sql="SUM(revenue) / COUNT(DISTINCT user_id)",
    description="Average revenue per user (ARPU)"
)
```

## MCP Tools

### define_custom_metric

Define a new custom metric.

**Parameters:**
- `name` (required): Unique metric name
- `type` (required): Metric type (count, count_distinct, sum, avg, ratio, custom_sql)
- `model` (required): Semantic model name
- `description` (optional): Human-readable description
- `dimension` (optional): Column to aggregate (for count_distinct, sum, avg)
- `numerator` (optional): Numerator metric (for ratio)
- `denominator` (optional): Denominator metric (for ratio)
- `sql` (optional): SQL expression (for custom_sql)
- `filters` (optional): Dictionary of filters
- `tags` (optional): List of tags for organization

**Example:**
```json
{
  "name": "power_users",
  "type": "count_distinct",
  "model": "users",
  "dimension": "user_id",
  "filters": {"login_count__gt": 100},
  "description": "Users with 100+ logins",
  "tags": ["engagement"]
}
```

**Returns:**
```json
{
  "status": "success",
  "metric": {
    "name": "power_users",
    "type": "count_distinct",
    "model": "users",
    "dimension": "user_id",
    "filters": {"login_count__gt": 100},
    "created_at": "2025-11-12T00:00:00",
    "tags": ["engagement"]
  },
  "message": "Metric 'power_users' created successfully"
}
```

### list_custom_metrics

List all custom metrics with optional filtering.

**Parameters:**
- `model` (optional): Filter by model name
- `tags` (optional): Filter by tags (returns metrics with any matching tag)

**Example:**
```json
{
  "model": "users",
  "tags": ["engagement"]
}
```

**Returns:**
```json
{
  "metrics": [
    {
      "name": "power_users",
      "type": "count_distinct",
      "model": "users",
      ...
    }
  ],
  "total_count": 1,
  "filtered_by": {
    "model": "users",
    "tags": ["engagement"]
  },
  "status": "success"
}
```

### delete_custom_metric

Delete a custom metric by name.

**Parameters:**
- `name` (required): Metric name to delete

**Example:**
```json
{
  "name": "temp_test_metric"
}
```

**Returns:**
```json
{
  "message": "Metric 'temp_test_metric' deleted successfully",
  "status": "success"
}
```

## Filter Operators

Filters use a special syntax: `dimension__operator`.

**Available operators:**
- `gt` - Greater than
- `gte` - Greater than or equal
- `lt` - Less than
- `lte` - Less than or equal
- `eq` - Equal
- `ne` - Not equal

**Examples:**
```python
# Login count greater than 100
filters={"login_count__gt": 100}

# Signup date after 2024-01-01
filters={"signup_date__gte": "2024-01-01"}

# Plan type equals "enterprise"
filters={"plan_type__eq": "enterprise"}

# Multiple filters
filters={
    "login_count__gt": 50,
    "plan_type": "paid",
    "created_date__gte": "2024-01-01"
}
```

## Usage Examples

### Scenario 1: Power User Analysis

```python
# Define power user metric
define_custom_metric(
    name="power_users",
    type="count_distinct",
    model="users",
    dimension="user_id",
    filters={"login_count__gte": 100},
    tags=["engagement"]
)

# Define super users (even more engaged)
define_custom_metric(
    name="super_users",
    type="count_distinct",
    model="users",
    dimension="user_id",
    filters={"login_count__gte": 500},
    tags=["engagement"]
)

# List all engagement metrics
list_custom_metrics(tags=["engagement"])
```

### Scenario 2: Revenue Analysis

```python
# Total revenue from enterprise customers
define_custom_metric(
    name="enterprise_revenue",
    type="sum",
    model="users",
    dimension="ltv",
    filters={"plan_type": "enterprise"},
    tags=["revenue", "enterprise"]
)

# Average revenue per enterprise customer
define_custom_metric(
    name="arpu_enterprise",
    type="custom_sql",
    model="users",
    sql="SUM(ltv) WHERE plan_type = 'enterprise' / COUNT(DISTINCT user_id) WHERE plan_type = 'enterprise'",
    tags=["revenue", "enterprise"]
)

# List all revenue metrics
list_custom_metrics(tags=["revenue"])
```

### Scenario 3: Conversion Funnel

```python
# Step 1: Define conversion metrics
define_custom_metric(
    name="signup_users",
    type="count_distinct",
    model="users",
    dimension="user_id",
    tags=["conversion"]
)

define_custom_metric(
    name="trial_users",
    type="count_distinct",
    model="users",
    dimension="user_id",
    filters={"signup_date__gte": "2024-01-01"},
    tags=["conversion"]
)

define_custom_metric(
    name="paid_users",
    type="count_distinct",
    model="users",
    dimension="user_id",
    filters={"plan_type__ne": "free"},
    tags=["conversion"]
)

# Step 2: Define conversion rates
define_custom_metric(
    name="trial_to_paid_rate",
    type="ratio",
    model="users",
    numerator="paid_users",
    denominator="trial_users",
    tags=["conversion"]
)
```

## Validation

All metrics are validated before creation:

1. **Model exists** - Validates the model name against available semantic models
2. **Dimension exists** - Validates dimension names against model schema
3. **Type-specific validation**:
   - Ratio metrics require both numerator and denominator
   - Custom SQL metrics require sql parameter
   - Count distinct, sum, avg require dimension parameter

**Example validation error:**
```json
{
  "status": "error",
  "error": "Dimension 'invalid_field' not found in model 'users'. Available: ['user_id', 'plan_type', 'industry', 'signup_date']"
}
```

## Persistence

Metrics are automatically persisted to:
```
semantic-layer/data/runtime_metrics.json
```

The file format:
```json
{
  "metrics": [
    {
      "name": "power_users",
      "type": "count_distinct",
      "model": "users",
      "dimension": "user_id",
      "filters": {"login_count__gt": 100},
      "created_at": "2025-11-12T00:00:00.000000",
      "created_by": "user",
      "tags": ["engagement"]
    }
  ],
  "last_updated": "2025-11-12T00:00:00.000000"
}
```

## Best Practices

1. **Use descriptive names** - `power_users` not `metric1`
2. **Add descriptions** - Help future you understand the metric
3. **Tag metrics** - Makes finding related metrics easier
4. **Start simple** - Use count_distinct before custom SQL
5. **Test filters** - Verify filters work as expected
6. **Clean up** - Delete metrics you no longer need

## Limitations

- Maximum 100 custom metrics per model (performance consideration)
- Metric names must be unique across all models
- Cannot override YAML-defined metrics
- Ratio metrics don't support complex calculations (use custom SQL instead)

## Troubleshooting

**Problem:** "Metric already exists"
- **Solution:** Use a different name or delete the existing metric first

**Problem:** "Dimension not found in model"
- **Solution:** Check model schema with `get_model_schema` tool

**Problem:** "Invalid metric type"
- **Solution:** Use one of: count, count_distinct, sum, avg, ratio, custom_sql

**Problem:** "Ratio metrics require numerator and denominator"
- **Solution:** Provide both numerator and denominator parameters

## Next Steps

After defining custom metrics, you can:

1. **Query them** - Use `query_model` tool with your custom metric
2. **Analyze them** - Use in workflow orchestration
3. **Share them** - Export runtime_metrics.json to share with team
4. **Refine them** - Delete and recreate with better definitions

## Support

For issues or questions:
- Check CLAUDE.md for system documentation
- Review test files for examples
- Check logs in ai_analyst.log
