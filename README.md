<a target="_blank" href="https://colab.research.google.com/github/advanced-computing/bouncy-banana/blob/main/Project.ipynb">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>

# Exploring Unemployment and Lifestyle Metrics in NYC
## Sophia Cain (sac2381) & Samuel Fu (sf3318) | Advanced Computing for Policy, Spring 2026
## Project Proposal
This project examines how unemployment trends intersect with key lifestyle
metrics, specifically housing security and public health, for New Yorkers
over time. We offer a comprehensive dashboard providing a high-level view
of all variables, alongside dedicated pages for deeper dives into each topic.
Interactive elements allow users to explore and analyze these trends
across different time periods and boroughs.
## Research Questions
- What are the effects of unemployment on the well-being of New Yorkers?
- What is the relationship between housing stability, physical health, and unemployment among New York City residents?
- Is there a correlation between unemployment and housing instability, specifically eviction rates, in New York City?
- Is there a correlation between unemployment and physical health outcomes in New York City
- How can policymakers use data on housing instability and physical health outcomes to design more effective social benefit programs for unemployed New Yorkers?
## Datasets
NYC Open Data: Health Survey
 - Updated Semi-Annually
 - Community health survey data covering different health indicators and access to care over time.

United States Department of Labor Unemployment Claims (FRED)
- Updated Weekly
- The Unemployment Insurance weekly claims data are used in current economic analysis of unemployment trends in the nation, and in each state. Initial claims measure emerging unemployment and continued weeks claimed measure the number of persons claiming unemployment benefits.

NYC Open Data: Eviction Records
- Updated Monthly
- Eviction filings, shelter census, and housing court data tracking housing instability across NYC boroughs.
## Project Setup
1. Clone the repository
``` bash
git clone https://github.com/advanced-computing/bouncy-banana.git
cd bouncy-banana 
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate        #Mac/Linux
venv\Scripts\activate           #Windows
```

3. Install Packages
Install all necessary packages by running:
``` bash
pip install -r requirements.txt
``` 

4. Set up secrets
- Our datasets are stored in Big Query, you will need to set the ```secrets.toml```
- Use instructions [here] (https://github.com/advanced-computing/course-materials/blob/main/docs/project.md)

3. Run the streamlit app locally
You can view the app locally by running ``` streamlit run streamlit_app.py``` in the command line
## Project Evolution
Initial Research Questions:
- What is the relationship between total New York City job postings and unemployment insurance claims over the past 10 years?
- How do the education levels of New Yorkers seeking jobs change in relation to unemployment over time?
- What is the relationship between unemployment and crime in New York City?

Initial Datasets:
- City of New York Job Postings (NYC Open Data)
- United States Department of Labor Unemployment Claims (FRED)
- City of New York Motor Vehicle Collisions - Crashes (NYC OpenData)

Issues Encountered:
- Some of our datasets and/or variables were not representative of what we wanted to measure
  - Vehicle collisions as a measure of NYC crime rates
- Some datasets are not updated regularly or updated too regularly
  - Job posting data is deleted after the job posting is filled
- We need to be able to isolate location or time within the dataset
  - BLS data on unemployment rates was for NYC county, but not NYC
## Future Improvements
1. More accurate unemployment metrics: supplement artificial estimates with official rates
2. Healthcare access metrics: add data on uninsured rates and delayed care among unemployed New Yorkers, which physical health risks
3. Provide an evidence base for evaluating whether existing benefit programs, like SNAP, Cash Assistance, and rental relief, are reaching the highest-need populations