#!/bin/bash
# Mercury DS Manager Take-Home - Claude Flow Hive-Mind Spawn Command

npx claude-flow@alpha hive-mind spawn \
  "Execute Mercury DS Manager take-home in SINGLE notebook (matt_strautmann_mercury_analysis.ipynb, ~25 cells total). Part 1 (cells 1-20): Exploratory analysis of organizations.csv (500 rows), adoption_funnel.csv (2000 rows), product_usage.csv (200k rows). Analyze: industry approval rates with statistical tests, segment product adoption patterns, churn measurement. Deliver 3-5 data-backed insights (n, p-value, effect size) and dashboard concept. Part 2 (cells 21-28): Design A/B test for industry-specific product recommendations grounded in Part 1 findings. Include: hypothesis, segmentation choice (industry_type vs industry) with data justification, sample size calculation (power 0.8, alpha 0.05), primary metric, guardrails (approval rate, time metrics), HTE analysis plan, decision framework. CRITICAL: Incremental cell-by-cell workflow - ONE task per cell, test code with 'uv run python' before adding to notebook, natural exploratory markdown (Let me check..., Hmm...), show failures/pivots, NO pre-planning 10 cells ahead. Working in Data_Science_Manager_Take_Home/ directory. Reference ../onboarding_experimentation_research.md for Brex case study and A/B testing framework. Max 5 hours." \
  --agents "data-scientist,ml-researcher,model-validator" \
  --topology hierarchical \
  --max-agents 4 \
  --memory-key mercury-takehome \
  --config claude-flow/CLAUDE.md

# Simplified version (if character limits):
# npx claude-flow@alpha hive-mind spawn \
#   "Mercury DS take-home: Single notebook (~25 cells). Part 1: Explore 3 datasets, find 3-5 insights. Part 2: Design A/B test experiment. Incremental workflow, ONE cell per task, test with uv first, show exploration. Data in Data_Science_Manager_Take_Home/. Max 5 hours." \
#   --agents "data-scientist,ml-researcher,model-validator" \
#   --topology hierarchical \
#   --memory-key mercury-takehome \
#   --config claude-flow/CLAUDE.md
