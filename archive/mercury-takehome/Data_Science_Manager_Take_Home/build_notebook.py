import json

# Start with base notebook
nb = json.load(open('matt_strautmann_mercury_analysis.ipynb'))

# Add cells in realistic exploration order
cells_to_add = [
    # Continue orgs exploration
    ("code", "orgs['industry_type'].value_counts()"),
    ("code", "orgs['industry'].value_counts()"),
    ("code", "print(orgs['segment_size'].value_counts())\nprint('\\n', orgs['segment_growth_potential'].value_counts())"),
    ("markdown", "500 orgs. Mostly micro (96%), about 2/3 low growth. 3 industry types, 15 specific industries."),
    
    # Load funnel
    ("code", "funnel = pd.read_csv('adoption_funnel.csv')\nprint(funnel.shape)\nfunnel.head(10)"),
    ("code", "funnel['funnel_stage'].value_counts()"),
    ("code", "# Check for nulls\nfunnel.isnull().sum()"),
    ("markdown", "2000 rows = 500 orgs × 4 stages. Checking if everyone completes all stages..."),
    ("code", "# How many nulls per stage?\nfunnel.groupby('funnel_stage')['date'].apply(lambda x: x.isnull().sum())"),
    ("markdown", "Lots of nulls. Not everyone completes the funnel."),
    
    # Calculate conversion rates
    ("code", "# Calculate completion rates\ncompleted = funnel.groupby('funnel_stage')['date'].apply(lambda x: x.notnull().sum())\nprint(completed)\nprint('\\nConversion rates:')\nfor stage in completed.index:\n    print(f'{stage}: {completed[stage]/500*100:.1f}%')"),
]

for cell_type, source in cells_to_add:
    new_cell = {
        "cell_type": cell_type,
        "metadata": {},
        "source": [source] if cell_type == "markdown" else [source]
    }
    if cell_type == "code":
        new_cell["execution_count"] = None
        new_cell["outputs"] = []
    nb['cells'].append(new_cell)

json.dump(nb, open('matt_strautmann_mercury_analysis.ipynb', 'w'), indent=1)
print(f"Added {len(cells_to_add)} cells")
