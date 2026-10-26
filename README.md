# EDA_Project
This is my EDA Project (Python-Streamlit)
Marine Species Climate Vulnerability Dashboard

An interactive Streamlit dashboard that explores how climate change affects marine species, built on the dataset from Boyce et al. (2022), Nature Climate Change.

Dataset

The dataset covers marine kingdoms, families and species, and shows how each one is affected by climate change in terms of sensitivity, vulnerability and exposure, and how well the animals adapt to these changes.

~25,000 marine species, each assessed under two scenarios: SSP126 (low emissions) and SSP585 (high emissions), giving ~50,000 records.
Key scores (0-1): Sensitivity, Exposure, Adaptation, Vulnerability.
Risk levels: N (none) < M (moderate) < H (high) < C (critical).
Ncells: number of grid cells a species occupies (range size).

File: Boyce_etal_2022_NATCC.csv

Dashboard structure
Sidebar: dataset description.
Main page: dataset overview and key metrics.
Data & Statistics tab: data preview, summary statistics, records per kingdom, missing values, data download.
View 1 - Impact on the Animal: sensitivity distribution, vulnerability by kingdom and scenario, correlation heatmap, species with the lowest/highest adaptation.
View 2 - Impact on its Region: exposure by scenario, range size vs sensitivity, share of species at high risk per scenario.
Each view has its own filters: climate scenario (dropdown), kingdom and overall climate risk (multiselect).
Key takeaways: patterns, relationships and outliers found in the analysis.
Key findings
The data is heavily biased toward one kingdom, Animalia, which affects overall averages.
Exposure and the share of species at high risk are higher under the high-emissions scenario.
Vulnerability is positively correlated with sensitivity (0.63) and exposure (0.59), and negatively with adaptation (-0.83). Adaptation is the strongest relationship.
The IQR method flagged 3,192 outliers (6.4%) in climate sensitivity; exposure had none.
These are correlations, not causation.
How to run
Install the requirements:
   pip install streamlit plotly pandas
Put Boyce_etal_2022_NATCC.csv in the same folder as app.py.
Run:
   streamlit run app.py
Project files
app.py: the Streamlit dashboard.
climateChange.ipynb: exploratory data analysis notebook (cleaning, statistics, visualizations).
Boyce_etal_2022_NATCC.csv: the dataset.
Source

Boyce, D. G., et al. (2022). Nature Climate Change.
