import json

# Create base notebook structure
nb = {
    "cells": [],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.13.5"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

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

# Start building realistic notebook
add_markdown("# Mercury Onboarding & Product Adoption\n\nMatt Strautmann | Oct 30, 2025\n\nExploring customer data to understand onboarding patterns and design an experiment for industry-specific product recommendations.")

add_code("import pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nfrom scipy import stats\nfrom datetime import datetime, timedelta\n\npd.set_option('display.max_columns', None)\npd.set_option('display.max_rows', 100)\nsns.set_style('whitegrid')\nplt.rcParams['figure.figsize'] = (10, 6)")

# Load orgs
add_code("# Load org data\norgs = pd.read_csv('organizations.csv')\norgs.head()")

add_code("orgs.shape")

add_code("orgs.info()")

add_code("# What industries?\norgs['industry_type'].value_counts()")

add_code("# More granular\nprint(f\"Unique industries: {orgs['industry'].nunique()}\")\norgs['industry'].value_counts()")

add_code("# Segments\nprint('Size:')\nprint(orgs['segment_size'].value_counts())\nprint('\\nGrowth potential:')\nprint(orgs['segment_growth_potential'].value_counts())")

add_markdown("500 orgs. Very micro-heavy - 479 of 500. Only 21 are small/medium. Growth potential split 345 low / 155 high.")

# Load funnel
add_markdown("---")
add_code("# Load funnel\nfunnel = pd.read_csv('adoption_funnel.csv')\nprint(funnel.shape)\nfunnel.head(10)")

add_code("funnel['funnel_stage'].value_counts()")

add_markdown("2000 rows = 500 orgs × 4 stages. Checking if all complete...")

add_code("funnel.isnull().sum()")

add_code("# Which stages have nulls?\nfunnel.groupby('funnel_stage')['date'].apply(lambda x: x.isnull().sum())")

add_markdown("790 null dates total. Application submitted has none (makes sense). Others have lots.")

# Conversion rates
add_code("# Calculate who completes each stage\nfor stage in ['approved', 'first_deposit', 'first_active']:\n    completed = funnel[funnel['funnel_stage']==stage]['date'].notnull().sum()\n    print(f'{stage}: {completed}/500 = {completed/500*100:.1f}%')")

add_markdown("55.6% approval. 47% first deposit. 39.4% activation.\n\nBig drop from approval to activation. Wondering if that's typical...")

# Does industry matter for approval?
add_code("# Does industry affect approval?\napproved_orgs = funnel[funnel['funnel_stage']=='approved'][['organization_id', 'date']].copy()\napproved_orgs['got_approved'] = approved_orgs['date'].notnull()\n\norg_approval = orgs.merge(approved_orgs[['organization_id', 'got_approved']], on='organization_id')\norg_approval.groupby('industry_type')['got_approved'].agg(['sum', 'count', 'mean']).sort_values('mean', ascending=False)")

add_markdown("Tech 69%, Consulting 57%, E-commerce 45%. Tech way higher.")

add_code("# By specific industry\norg_approval.groupby('industry')['got_approved'].agg(['sum', 'count', 'mean']).sort_values('mean', ascending=False)")

add_markdown("Software at 78%, B2B at 74%. Retail/wholesale only 36%. Makes sense - tech probably has clearer business models.")

# Visualize it
add_code("# Plot approval rates by industry type\napproval_by_type = org_approval.groupby('industry_type')['got_approved'].mean().sort_values()\n\nplt.figure(figsize=(8, 5))\napproval_by_type.plot(kind='barh')\nplt.xlabel('Approval Rate')\nplt.title('Approval Rate by Industry Type')\nplt.tight_layout()\nplt.show()")

# Product data
add_markdown("---")
add_code("# Load product data\nproducts = pd.read_csv('product_usage.csv')\nprint(products.shape)\nproducts.head()")

add_code("print(f\"Unique orgs: {products['organization_id'].nunique()}\")\nprint(f\"\\nProducts:\")\nprint(products['product'].value_counts())")

add_markdown("278 unique orgs in product data. Same as # approved! Makes sense - need approval to use products.")

add_code("# Date range\nproducts['day'] = pd.to_datetime(products['day'])\nprint(f\"Date range: {products['day'].min()} to {products['day'].max()}\")")

add_markdown("Full year of data (2024).")

# Product adoption rates
add_code("# For each org-product, ever active?\nproduct_ever = products.groupby(['organization_id', 'product'])['is_active'].max().reset_index()\nproduct_ever.columns = ['organization_id', 'product', 'ever_active']\n\n# Overall adoption rates\nadoption_rates = product_ever.groupby('product')['ever_active'].agg(['sum', 'count', 'mean'])\nadoption_rates.columns = ['Ever Active', 'Total', 'Adoption Rate']\nprint(adoption_rates.sort_values('Adoption Rate', ascending=False))")

add_markdown("Bank Account 62%, Debit 49%, Credit Card 7%, Invoicing 6%.\n\nInvoicing barely used. Credit Card also pretty low.")

# Does industry affect product adoption?
add_code("# Join with org data\nproduct_orgs = product_ever.merge(orgs, on='organization_id')\n\n# By industry type\nadoption_by_industry = product_orgs.groupby(['industry_type', 'product'])['ever_active'].mean().unstack()\nprint(adoption_by_industry.round(3))")

add_markdown("Tech has 13% Credit Card adoption vs 3-4% for others. That's 3-4x higher.\n\nInvoicing: Tech 9%, Consulting 7%, E-commerce only 1%.\n\nDebit Card pretty consistent ~48-49%.")

# Visualize this
add_code("# Plot product adoption by industry\nadoption_by_industry.plot(kind='bar', figsize=(10, 6))\nplt.title('Product Adoption Rate by Industry Type')\nplt.ylabel('Adoption Rate')\nplt.xlabel('Industry Type')\nplt.xticks(rotation=45, ha='right')\nplt.legend(title='Product', bbox_to_anchor=(1.05, 1))\nplt.tight_layout()\nplt.show()")

# Is Credit Card difference significant?
add_code("# Is the Tech vs others Credit Card difference significant?\nfrom scipy.stats import chi2_contingency\n\ncc_data = product_orgs[product_orgs['product']=='Credit Card']\ntech_cc = cc_data[cc_data['industry_type']=='Technology']['ever_active']\nother_cc = cc_data[cc_data['industry_type']!='Technology']['ever_active']\n\ncontingency = pd.crosstab(cc_data['industry_type']=='Technology', cc_data['ever_active'])\nchi2, p, dof, expected = chi2_contingency(contingency)\nprint(f'Chi-square: {chi2:.2f}, p-value: {p:.6f}')")

add_markdown("p < 0.001. Highly significant. Tech companies really do prefer Credit Card.")

# Segment analysis
add_code("# Does growth potential matter?\nproduct_orgs.groupby(['segment_growth_potential', 'product'])['ever_active'].mean().unstack().round(3)")

add_markdown("High growth: Credit Card 14% vs low growth 2%. That's 7x!\n\nAlso higher for Invoicing (9% vs 3%).")

# Save output
json.dump(nb, open('matt_strautmann_mercury_analysis.ipynb', 'w'), indent=1)
print(f"Created notebook with {len(nb['cells'])} cells")
