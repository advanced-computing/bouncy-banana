import streamlit as st

page_1 = st.Page("pages/1_Unemployment_Dashboard.py", title="NYC Dashboard")
page_2 = st.Page("pages/2_NYC_Unemployment.py", title="NYC Unemployment Dashboard")
page_3 = st.Page("pages/3_NYC_Evictions.py", title="NYC Eviction Dashboard")
page_4 = st.Page("pages/4_NYC_Health.py", title="NYC Health Dashboard")
page_5 = st.Page("pages/5_Project_Documentation.py", title="Project Documentation")
page_6 = st.Page("pages/6_Combined_Analysis.py", title="Unemployment & Evictions Combined")

pg = st.navigation([page_1, page_2, page_3, page_4, page_5, page_6])
pg.run()
