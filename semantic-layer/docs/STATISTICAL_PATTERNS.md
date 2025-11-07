# Statistical Patterns for AI Analyst

**Source**: Mercury project learnings + Research on A/B testing frameworks

---

## Core Principle: Statistical Rigor by Default

**Goal**: Automatically run statistical tests when comparing groups, showing correlations, or making claims.

**User should see**: "Tech customers 2x higher LTV (p<0.001, n=1,523 vs n=892, Cohen's d=0.8)"

**NOT**: "Tech customers have higher LTV"

---

## Pattern 1: Auto Sample Size Validation

### When to Apply
Every time you show aggregated metrics by dimension (industry, plan type, cohort, etc.)

### Implementation

```python
def validate_sample_size(result: DataFrame, dimension_col: str):
    """Check if sample sizes are sufficient for confidence"""

    sample_sizes = result.groupby(dimension_col).size()

    for group, n in sample_sizes.items():
        if n < 10:
            yield f"⛔ {group}: n={n} (too small, need n≥30)"
        elif n < 30:
            yield f"⚠️ {group}: n={n} (marginal, interpret with caution)"
        elif n < 100:
            yield f"💡 {group}: n={n} (acceptable)"
        else:
            yield f"✅ {group}: n={n} (good sample)"
```

### Example Usage

```python
# User asks: "What's DAU by plan type?"
result = query_model('engagement', dimensions=['plan_type'], measures=['dau'])

# Auto-validate sample sizes
validations = validate_sample_size(result, 'plan_type')

# Output:
# ✅ free: n=450 (good sample)
# ✅ starter: n=120 (good sample)
# 💡 pro: n=85 (acceptable)
# ⚠️ enterprise: n=12 (marginal, interpret with caution)
```

---

## Pattern 2: Auto Significance Testing

### When to Apply
When comparing groups on any metric

### Chi-Square Test (Categorical Outcomes)

```python
from scipy.stats import chi2_contingency

def auto_chi_square_test(result: DataFrame, dimension_col: str, metric_col: str):
    """Automatically run chi-square test when comparing groups"""

    # Create contingency table
    contingency = pd.crosstab(
        result[dimension_col],
        result[metric_col]  # Binary: active/inactive, churned/retained, etc.
    )

    # Run test
    chi2, p_value, dof, expected = chi2_contingency(contingency)

    return {
        "test": "chi-square",
        "statistic": chi2,
        "p_value": p_value,
        "dof": dof,
        "significant": p_value < 0.05,
        "interpretation": _interpret_p_value(p_value)
    }
```

### T-Test (Continuous Outcomes)

```python
from scipy.stats import ttest_ind

def auto_t_test(result: DataFrame, dimension_col: str, metric_col: str):
    """Automatically run t-test when comparing group means"""

    groups = result.groupby(dimension_col)[metric_col].apply(list)

    if len(groups) == 2:
        group1, group2 = groups.values()
        t_stat, p_value = ttest_ind(group1, group2)

        return {
            "test": "two-sample t-test",
            "statistic": t_stat,
            "p_value": p_value,
            "significant": p_value < 0.05,
            "interpretation": _interpret_p_value(p_value)
        }
    else:
        # More than 2 groups: use ANOVA
        from scipy.stats import f_oneway
        f_stat, p_value = f_oneway(*groups.values())

        return {
            "test": "ANOVA",
            "statistic": f_stat,
            "p_value": p_value,
            "significant": p_value < 0.05
        }
```

### P-Value Interpretation

```python
def _interpret_p_value(p: float) -> str:
    """Human-readable p-value interpretation"""

    if p < 0.001:
        return "Highly significant (p<0.001)"
    elif p < 0.01:
        return "Very significant (p<0.01)"
    elif p < 0.05:
        return "Significant (p<0.05)"
    elif p < 0.10:
        return "Marginally significant (p<0.10)"
    else:
        return f"Not significant (p={p:.3f})"
```

---

## Pattern 3: Effect Size Calculation

### Why Effect Size Matters

**Problem**: p-value only tells you if difference is real, not if it matters.

**Example**: With n=10,000, a 0.1% difference can be "statistically significant" but practically meaningless.

**Solution**: Always calculate effect size alongside p-value.

### Cohen's d (For Means)

```python
def cohens_d(group1: list, group2: list) -> float:
    """Calculate Cohen's d effect size"""

    mean1, mean2 = np.mean(group1), np.mean(group2)
    std1, std2 = np.std(group1, ddof=1), np.std(group2, ddof=1)
    n1, n2 = len(group1), len(group2)

    # Pooled standard deviation
    pooled_std = np.sqrt(((n1-1)*std1**2 + (n2-1)*std2**2) / (n1+n2-2))

    return (mean1 - mean2) / pooled_std

def interpret_cohens_d(d: float) -> str:
    """Interpret Cohen's d magnitude"""

    abs_d = abs(d)
    if abs_d < 0.2:
        return "negligible"
    elif abs_d < 0.5:
        return "small"
    elif abs_d < 0.8:
        return "medium"
    else:
        return "large"
```

### Cohen's h (For Proportions)

```python
def cohens_h(p1: float, p2: float) -> float:
    """Calculate Cohen's h for proportion differences"""

    phi1 = 2 * np.arcsin(np.sqrt(p1))
    phi2 = 2 * np.arcsin(np.sqrt(p2))

    return phi1 - phi2

# Interpretation same as Cohen's d
```

### Relative Difference (Business Metric)

```python
def relative_difference(value1: float, value2: float) -> dict:
    """Calculate relative difference (% change)"""

    absolute_diff = value1 - value2
    relative_diff = (value1 - value2) / value2 if value2 != 0 else float('inf')

    return {
        "absolute": absolute_diff,
        "relative": relative_diff,
        "percentage": relative_diff * 100,
        "multiplier": value1 / value2 if value2 != 0 else float('inf')
    }
```

---

## Pattern 4: Confidence Intervals

### When to Show

Always, for any estimated metric.

### Implementation

```python
from scipy.stats import t

def confidence_interval(data: list, confidence=0.95) -> tuple:
    """Calculate confidence interval for mean"""

    n = len(data)
    mean = np.mean(data)
    std = np.std(data, ddof=1)
    se = std / np.sqrt(n)

    # t-distribution critical value
    t_crit = t.ppf((1 + confidence) / 2, n - 1)

    margin = t_crit * se

    return (mean - margin, mean + margin)

def format_ci(mean: float, ci: tuple, confidence=0.95) -> str:
    """Format for display"""

    return f"{mean:.1f} (95% CI: {ci[0]:.1f}-{ci[1]:.1f})"
```

### Example Output

```python
# User asks: "What's average session duration?"
durations = [45, 52, 38, 61, 47, 55, 43, ...]  # seconds

mean_duration = np.mean(durations)
ci = confidence_interval(durations)

# Output:
"Average session duration: 48.2 seconds (95% CI: 45.1-51.3)"
```

---

## Pattern 5: Comprehensive Comparison Output

### Template

When comparing groups, always show:
1. Raw values
2. Sample sizes
3. Statistical significance (p-value)
4. Effect size
5. Confidence intervals
6. Business interpretation

### Implementation

```python
def comprehensive_comparison(result: DataFrame, dimension: str, metric: str):
    """Generate full statistical comparison"""

    groups = result.groupby(dimension)[metric].apply(list).to_dict()

    # Calculate stats for each group
    stats = {}
    for group_name, values in groups.items():
        stats[group_name] = {
            "n": len(values),
            "mean": np.mean(values),
            "std": np.std(values, ddof=1),
            "ci": confidence_interval(values)
        }

    # If 2 groups, run pairwise comparison
    if len(groups) == 2:
        g1_name, g2_name = list(groups.keys())
        g1_vals, g2_vals = groups[g1_name], groups[g2_name]

        t_stat, p_value = ttest_ind(g1_vals, g2_vals)
        effect_size = cohens_d(g1_vals, g2_vals)
        rel_diff = relative_difference(stats[g1_name]["mean"], stats[g2_name]["mean"])

        return {
            "groups": stats,
            "comparison": {
                "test": "two-sample t-test",
                "p_value": p_value,
                "significant": p_value < 0.05,
                "effect_size": effect_size,
                "effect_magnitude": interpret_cohens_d(effect_size),
                "relative_difference": rel_diff
            },
            "interpretation": _generate_interpretation(stats, g1_name, g2_name, p_value, effect_size, rel_diff)
        }

    return {"groups": stats}

def _generate_interpretation(stats, g1, g2, p_value, effect_size, rel_diff):
    """Natural language interpretation"""

    g1_mean = stats[g1]["mean"]
    g2_mean = stats[g2]["mean"]
    g1_n = stats[g1]["n"]
    g2_n = stats[g2]["n"]

    if p_value < 0.05:
        significance = _interpret_p_value(p_value)
        magnitude = interpret_cohens_d(effect_size)

        return (
            f"{g1} {rel_diff['multiplier']:.1f}x higher than {g2} "
            f"({g1_mean:.1f} vs {g2_mean:.1f}, "
            f"{significance}, "
            f"{magnitude} effect size, "
            f"n={g1_n} vs n={g2_n})"
        )
    else:
        return f"No significant difference between {g1} and {g2} (p={p_value:.3f})"
```

### Example Output

```python
# User asks: "Compare DAU between free and paid users"

result = comprehensive_comparison(
    data,
    dimension='plan_type',
    metric='daily_active_users'
)

# Output:
{
  "groups": {
    "free": {"n": 450, "mean": 1250, "std": 320, "ci": (1220, 1280)},
    "paid": {"n": 120, "mean": 2800, "std": 580, "ci": (2700, 2900)}
  },
  "comparison": {
    "test": "two-sample t-test",
    "p_value": 0.0001,
    "significant": true,
    "effect_size": 0.85,
    "effect_magnitude": "large",
    "relative_difference": {"multiplier": 2.24}
  },
  "interpretation": "paid 2.2x higher than free (2800 vs 1250, Highly significant (p<0.001), large effect size, n=120 vs n=450)"
}
```

---

## Pattern 6: Guardrail Metrics

### Purpose

Ensure no unintended harm despite positive primary metric.

### Framework (from Airbnb)

```python
class GuardrailMonitor:
    """Monitor guardrail metrics during analysis"""

    def __init__(self, guardrails: dict):
        """
        guardrails = {
            'metric_name': {
                'threshold': -0.03,  # Max acceptable decrease
                'direction': 'up'  # or 'down', 'neutral'
            }
        }
        """
        self.guardrails = guardrails

    def check(self, results: dict) -> dict:
        """Check if any guardrails violated"""

        violations = []

        for metric, config in self.guardrails.items():
            if metric in results:
                change = results[metric]['change']
                threshold = config['threshold']
                direction = config['direction']

                if direction == 'up' and change < threshold:
                    violations.append(f"⛔ {metric} decreased {change:.1%} (limit: {threshold:.1%})")
                elif direction == 'down' and change > -threshold:
                    violations.append(f"⛔ {metric} increased {change:.1%} (limit: {-threshold:.1%})")

        return {
            "passed": len(violations) == 0,
            "violations": violations
        }
```

### Example (Product Analytics)

```python
# Primary metric: Feature adoption rate
# Guardrails: Ensure no harm to activation, retention, engagement

guardrails = GuardrailMonitor({
    'activation_rate': {'threshold': -0.03, 'direction': 'up'},  # Must not drop >3%
    'day7_retention': {'threshold': -0.05, 'direction': 'up'},   # Must not drop >5%
    'dau': {'threshold': -0.02, 'direction': 'up'}               # Must not drop >2%
})

# After experiment
results = {
    'feature_adoption': {'change': 0.12},  # +12% (primary metric)
    'activation_rate': {'change': -0.01},  # -1% (within guardrail)
    'day7_retention': {'change': -0.08},   # -8% (VIOLATED!)
    'dau': {'change': 0.01}                # +1% (fine)
}

check = guardrails.check(results)
# Output:
# {
#   "passed": False,
#   "violations": ["⛔ day7_retention decreased -8.0% (limit: -5.0%)"]
# }
# Recommendation: Do NOT ship - retention harm outweighs adoption gain
```

---

## Pattern 7: HTE (Heterogeneous Treatment Effects)

### Purpose

Detect if different subgroups respond differently to the same treatment.

### Implementation

```python
def detect_hte(result: DataFrame, treatment_col: str, outcome_col: str, subgroup_col: str):
    """Detect heterogeneous treatment effects by subgroup"""

    hte_results = []

    for subgroup in result[subgroup_col].unique():
        subgroup_data = result[result[subgroup_col] == subgroup]

        # Compare treatment vs control within this subgroup
        treated = subgroup_data[subgroup_data[treatment_col] == 1][outcome_col]
        control = subgroup_data[subgroup_data[treatment_col] == 0][outcome_col]

        if len(treated) > 0 and len(control) > 0:
            t_stat, p_value = ttest_ind(treated, control)
            effect = np.mean(treated) - np.mean(control)
            rel_effect = effect / np.mean(control) if np.mean(control) != 0 else float('inf')

            hte_results.append({
                "subgroup": subgroup,
                "n_treated": len(treated),
                "n_control": len(control),
                "effect": effect,
                "relative_effect": rel_effect,
                "p_value": p_value,
                "significant": p_value < 0.05
            })

    return pd.DataFrame(hte_results).sort_values('relative_effect', ascending=False)
```

### Example Output

```python
# Question: "Does industry-specific onboarding work equally for all industries?"

hte = detect_hte(
    experiment_data,
    treatment_col='got_personalized_onboarding',
    outcome_col='activated',
    subgroup_col='industry'
)

# Output:
#   subgroup    n_treated  n_control  effect  relative_effect  p_value  significant
#   fintech          45         50    0.25         0.50      0.002        True
#   saas             60         55    0.15         0.30      0.015        True
#   ecommerce        30         35   -0.05        -0.10      0.450        False

# Interpretation:
# "Treatment works for fintech (+50%) and SaaS (+30%), but not for e-commerce (-10%, n.s.)"
# Recommendation: Selective rollout to fintech and SaaS only
```

---

## Summary: Auto-Statistical Testing Flow

```python
class StatisticalAnalyst:
    """Automatically apply statistical rigor to all comparisons"""

    def analyze(self, query_result: DataFrame):
        """Full statistical analysis pipeline"""

        # 1. Validate sample sizes
        sample_validation = self.validate_samples(query_result)

        # 2. Run appropriate statistical test
        if self.is_comparison(query_result):
            test_result = self.run_test(query_result)

            # 3. Calculate effect size
            effect_size = self.calculate_effect_size(query_result)

            # 4. Generate confidence intervals
            confidence_intervals = self.calculate_cis(query_result)

            # 5. Check guardrails (if applicable)
            guardrail_check = self.check_guardrails(query_result)

            # 6. Detect HTE (if subgroups present)
            hte_analysis = self.detect_hte(query_result)

        # 7. Generate comprehensive interpretation
        interpretation = self.generate_interpretation(
            query_result,
            sample_validation,
            test_result,
            effect_size,
            confidence_intervals,
            guardrail_check,
            hte_analysis
        )

        return interpretation
```

---

**Last Updated**: 2025-11-05
**Source**: Mercury project learnings + A/B testing research
**Status**: Design patterns for AI Analyst implementation
