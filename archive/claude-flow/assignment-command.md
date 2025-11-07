# Mercury DS Take-Home - Claude Flow Hive-Mind Command

## Recommended Command (Run from claude-flow/ directory)

```bash
npx claude-flow@alpha hive-mind spawn \
  "Complete Mercury DS Manager take-home in single notebook matt_strautmann_mercury_analysis.ipynb with ~25 cells total. Part 1 (cells 1-20): Explore organizations.csv (500 rows), adoption_funnel.csv (2k rows), product_usage.csv (200k rows). Analyze industry approval rates with statistical tests, segment product adoption patterns, churn measurement. Deliver 3-5 data-backed insights (n, p-value, effect size) and dashboard concept. Part 2 (cells 21-28): Design A/B test for industry-specific product recommendations grounded in Part 1 findings. Include hypothesis, segmentation choice (industry_type vs industry) with data justification, sample size calculation (power 0.8, alpha 0.05), guardrail metrics, HTE analysis plan, decision framework. CRITICAL: Incremental workflow - ONE task per cell, test code with 'uv run python' before adding to notebook, natural exploratory markdown showing failures/pivots/questions, NO pre-planning cells ahead. Working in ../Data_Science_Manager_Take_Home/. Reference ../onboarding_experimentation_research.md for Brex case study and A/B testing framework. Max 5 hours." \
  --claude
```

## Shorter Version (If Character Limit Issues)

```bash
npx claude-flow@alpha hive-mind spawn \
  "Single notebook (~25 cells): Part 1 explore 3 datasets (orgs 500, funnel 2k, usage 200k rows), find 3-5 insights with stats. Part 2 design A/B test experiment grounded in Part 1. Incremental workflow, ONE cell per task, test with uv first, show exploration. In ../Data_Science_Manager_Take_Home/. Max 5 hours." \
  --claude
```

## Without Claude Code CLI (Background Execution)

```bash
npx claude-flow@alpha hive-mind spawn \
  "Complete Mercury DS Manager take-home in single notebook matt_strautmann_mercury_analysis.ipynb with ~25 cells total. Part 1 (cells 1-20): Explore organizations.csv (500 rows), adoption_funnel.csv (2k rows), product_usage.csv (200k rows). Analyze industry approval rates with statistical tests, segment product adoption patterns, churn measurement. Deliver 3-5 data-backed insights (n, p-value, effect size) and dashboard concept. Part 2 (cells 21-28): Design A/B test for industry-specific product recommendations grounded in Part 1 findings. Include hypothesis, segmentation choice (industry_type vs industry) with data justification, sample size calculation (power 0.8, alpha 0.05), guardrail metrics, HTE analysis plan, decision framework. CRITICAL: Incremental workflow - ONE task per cell, test code with 'uv run python' before adding to notebook, natural exploratory markdown showing failures/pivots/questions, NO pre-planning cells ahead. Working in ../Data_Science_Manager_Take_Home/. Reference ../onboarding_experimentation_research.md for Brex case study and A/B testing framework. Max 5 hours."
```

## What This Does

The `hive-mind spawn` command:

1. **Reads CLAUDE.md** in current directory (claude-flow/) for all configuration
2. **Spawns intelligent swarm** that coordinates multi-agent work
3. **Opens Claude Code CLI** (with `--claude` flag) for interactive execution
4. **Executes in context** - all agents have access to CLAUDE.md rules and dataset schemas
5. **Generates notebook** incrementally in ../Data_Science_Manager_Take_Home/matt_strautmann_mercury_analysis.ipynb

## Key Flag

- `--claude`: Opens Claude Code CLI for interactive execution (RECOMMENDED)
  - Without this flag: Runs in background, harder to monitor
  - With this flag: You see the work happening in real-time

## After Execution

Check swarm status:
```bash
npx claude-flow@alpha hive-mind status

# View metrics
npx claude-flow@alpha hive-mind metrics
```

## Notes

- Run from `claude-flow/` directory so CLAUDE.md is found automatically
- The objective string contains all assignment details
- CLAUDE.md provides full context (incremental workflow rules, dataset schemas, research references)
- Paths are relative from claude-flow/ directory (../Data_Science_Manager_Take_Home/)
- Single notebook output: matt_strautmann_mercury_analysis.ipynb with ~25 cells
