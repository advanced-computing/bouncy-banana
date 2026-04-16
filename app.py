import streamlit as st

page_1 = st.Page("pages/1_Project_Overview.py", title="Project Overview")
page_2 = st.Page("pages/2_NYC_Unemployment.py", title="NYC Unemployment")
page_3 = st.Page("pages/3_NYC_Evictions.py", title="NYC Evictions")

pg = st.navigation([page_1, page_2, page_3])
pg.run()
