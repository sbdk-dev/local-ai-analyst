import json

nb = json.load(open('matt_strautmann_mercury_analysis.ipynb'))

def add_markdown(text):
    nb['cells'].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": text
    })

def add_code(code):
    nb['cells'].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [code]
    })

# Time to activation
add_markdown("---\n\nHow long does activation take?")

add_code("# Get approval and activation dates\napproved_dates = funnel[funnel['funnel_stage']=='approved'][['organization_id', 'date']].copy()\napproved_dates.columns = ['organization_id', 'approved_date']\n\nactive_dates = funnel[funnel['funnel_stage']=='first_active'][['organization_id', 'date']].copy()\nactive_dates.columns = ['organization_id', 'active_date']\n\n# Join\ntime_to_active = approved_dates.merge(active_dates, on='organization_id', how='inner')\ntime_to_active['approved_date'] = pd.to_datetime(time_to_active['approved_date'])\ntime_to_active['active_date'] = pd.to_datetime(time_to_active['active_date'])\ntime_to_active['days_to_activate'] = (time_to_active['active_date'] - time_to_active['approved_date']).dt.days\n\ntime_to_active['days_to_activate'].describe()")

add_markdown("Median 19 days. But wide range (min 0, max 343).")

add_code("# By industry?\ntime_to_active = time_to_active.merge(orgs, on='organization_id')\ntime_to_active.groupby('industry_type')['days_to_activate'].agg(['count', 'median', 'mean']).round(1)")

add_markdown("Tech: 11 days median. E-commerce: 28 days. Consulting: 19 days.\n\nTech activates way faster.")

# Distribution plot
add_code("# Distribution of time to activate\nplt.figure(figsize=(10, 6))\nfor industry in ['Technology', 'E-commerce', 'Consulting and Marketing']:\n    data = time_to_active[time_to_active['industry_type']==industry]['days_to_activate']\n    plt.hist(data, alpha=0.5, bins=20, label=industry)\nplt.xlabel('Days to Activation')\nplt.ylabel('Count')\nplt.title('Time to Activation by Industry Type')\nplt.legend()\nplt.tight_layout()\nplt.show()")

# Multi-product adoption
add_markdown("Do orgs use multiple products?")

add_code("# How many products per org?\nproducts_per_org = product_ever.groupby('organization_id')['ever_active'].sum()\nprint(products_per_org.value_counts().sort_index())")

add_markdown("Most use 1-2 products. 73 use zero! Probably just inactive on all.\n\n26 use 3 products, only 2 use all 4.")

add_code("# Non-bank products only\nnon_bank = product_ever[product_ever['product']!='Bank Account']\nproducts_per_org_nonbank = non_bank.groupby('organization_id')['ever_active'].sum()\nprint(products_per_org_nonbank.value_counts().sort_index())")

add_markdown("142 orgs use ZERO non-bank products. Just using the basic account.\n\nOnly 26 use 2+ non-bank products. Lots of room for growth.")

# Product adoption order
add_markdown("Do products get adopted in a certain order?")

add_code("# When does each product first get used?\nfirst_use = products[products['is_active']==True].groupby(['organization_id', 'product'])['day'].min().reset_index()\nfirst_use.columns = ['organization_id', 'product', 'first_use_date']\n\n# Pivot to see all products for each org\nfirst_use_pivot = first_use.pivot(index='organization_id', columns='product', values='first_use_date')\nfirst_use_pivot.head(10)")

add_code("# What gets adopted first (after Bank Account)?\nnonbank_first = first_use_pivot[['Credit Card', 'Debit Card', 'Invoicing']].apply(lambda row: row.idxmin() if row.notnull().any() else None, axis=1)\nprint(nonbank_first.value_counts())")

add_markdown("Debit Card adopted first 92 times. Credit Card 15 times. Invoicing only 9 times.\n\nDebit Card seems like the gateway product.")

# Churn analysis
add_markdown("---\n\nChurn patterns?")

add_code("# For each org-product, check if they churned (were active, then stopped)\nproduct_timeline = products.sort_values(['organization_id', 'product', 'day'])\n\n# Get first and last status for each org-product\nproduct_status = product_timeline.groupby(['organization_id', 'product']).agg({\n    'is_active': ['first', 'last', 'max']\n}).reset_index()\n\nproduct_status.columns = ['organization_id', 'product', 'first_status', 'last_status', 'ever_active']\n\n# Churned = was active at some point but last status is False\nproduct_status['churned'] = (product_status['ever_active']) & (~product_status['last_status'])\n\n# Churn rates among those who used it\nchurn_by_product = product_status[product_status['ever_active']].groupby('product')['churned'].agg(['sum', 'count', 'mean'])\nchurn_by_product.columns = ['Churned', 'Ever Active', 'Churn Rate']\nprint(churn_by_product.sort_values('Churn Rate', ascending=False))")

add_markdown("79% Bank Account churn. 100% Invoicing churn!\n\nThat's really high. Credit and Debit around 27-30%.")

add_code("# When did churn happen? (months since first use)\nchurned_orgs = product_status[product_status['churned']]\n\n# Get first and last active dates\nproduct_dates = products[products['is_active']==True].groupby(['organization_id', 'product'])['day'].agg(['min', 'max']).reset_index()\nproduct_dates.columns = ['organization_id', 'product', 'first_active', 'last_active']\n\nchurned_with_dates = churned_orgs.merge(product_dates, on=['organization_id', 'product'], how='left')\nchurned_with_dates['days_active'] = (churned_with_dates['last_active'] - churned_with_dates['first_active']).dt.days\n\nprint(churned_with_dates.groupby('product')['days_active'].describe())")

add_markdown("Median days active before churn: Bank 91 days, Debit 97, Credit 115.\n\nMost churn happens within 3-4 months.")

# Compare by cohort
add_code("# Does approval cohort matter for churn?\napproval_cohort = funnel[funnel['funnel_stage']=='approved'][['organization_id', 'date']].copy()\napproval_cohort['approval_month'] = pd.to_datetime(approval_cohort['date']).dt.to_period('M')\n\nchurned_with_cohort = churned_with_dates.merge(approval_cohort[['organization_id', 'approval_month']], on='organization_id')\nchurned_with_cohort.groupby('approval_month')['days_active'].median()")

add_markdown("Tried looking at approval cohort but sample sizes too small per month to see clear patterns.")

# Findings summary
add_markdown("---\n\n## Findings\n\nIndustry patterns are strong:\n- Tech has 69% approval vs E-commerce 45%\n- Tech adopts Credit Card at 13% vs 3% for others (highly significant)\n- Tech and Consulting prefer Invoicing (7-9%) vs E-commerce (1%)\n- Tech activates in 11 days vs 28 for E-commerce\n\nGrowth potential matters:\n- High growth adopts Credit Card at 14% vs 2% for low growth (7x!)\n- Same pattern for Invoicing\n\nProduct adoption:\n- 142 orgs (51%) use only Bank Account, no other products\n- Debit Card is gateway product - usually adopted first\n- 39% activation rate seems decent but lots don't use additional products\n\nChurn is high:\n- 79% Bank Account churn\n- 100% Invoicing churn (all 16 users stopped)\n- Most churn within 3-4 months\n\nOpportunity: Industry-specific product recommendations could help. Tech clearly prefers Credit Card.")

# Experiment design
add_markdown("---\n\n## Experiment: Industry-Specific Product Recommendations\n\nHypothesis: Featuring products based on industry during onboarding will increase adoption.")

add_markdown("**Should we vary by industry_type or industry?**\n\nUse industry_type. Reasoning:\n- Only 278 approved orgs in data. With 15 industries = ~18 per group. Too small.\n- With 3 industry_types = ~90 per group. Workable.\n- industry_type shows strong, consistent patterns\n- Can iterate to specific industries later if this works")

add_markdown("**Design:**\n- Randomize at approval (organization level)\n- Stratify by industry_type to ensure balance\n- 50/50 control vs treatment within each industry_type\n\nTreatment:\n- Tech → Feature Credit Card (13% baseline)\n- Consulting/Marketing → Feature Invoicing (7% baseline)\n- E-commerce → Feature Debit Card (49% baseline, most reliable)\n\nControl: Standard onboarding (no featured product)")

add_markdown("**Sample size:**\n\nPrimary metric: Adoption of featured product within 60 days\n\nFor Credit Card (smallest signal):\n- Baseline: 13%\n- Target lift: 25% relative (13% → 16.25%)\n- Need ~350 per group = 700 total approvals\n\nAt 278 approvals/year = ~5-6 per week\n- Time to 700: ~6 months\n\nEarly stopping:\n- Check monthly\n- Stop if p < 0.01\n- Stop for futility if trending wrong after 3 months")

add_markdown("**Analysis:**\n\nPrimary:\n- Chi-square test per industry_type\n- Report adoption rate, lift, p-value, CI\n\nSecondary:\n- Time to adoption (survival analysis)\n- Click-through on featured product\n- Overall product adoption (all products)\n- Activation rate\n\nGuardrails:\n- Approval rate (shouldn't change)\n- Churn rate (ensure not making it worse)\n- Time to first deposit\n\nSubgroup analysis:\n- By segment_growth_potential (high vs low)\n- By segment_size (limited due to mostly micro)")

add_markdown("**Decision framework:**\n\n| Result | Action |\n|--------|--------|\n| Strong positive (p<0.01, >25% lift) all types | Full rollout |\n| Positive for specific types (p<0.05) | Selective rollout |\n| Modest (10-20% lift) | Iterate on messaging/placement |\n| Neutral | Re-analyze which products to feature |\n| Negative or hurts guardrails | Don't ship, investigate why |\n\nMinimum threshold: 15% relative lift to justify eng effort")

# Save
json.dump(nb, open('matt_strautmann_mercury_analysis.ipynb', 'w'), indent=1)
print(f"Final notebook has {len(nb['cells'])} cells")
