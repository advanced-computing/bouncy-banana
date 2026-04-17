import streamlit as st

page_1 = st.Page("pages/1_Project_Overview.py", title="Project Overview")
page_2 = st.Page("pages/2_NYC_Unemployment.py", title="Long-Term Unemployment")
page_3 = st.Page("pages/3_NYC_Evictions.py", title="Housing Evictions")
page_4 = st.Page("pages/4_NYC_Health.py", title="Health")

pg = st.navigation([page_1, page_2, page_3, page_4])
pg.run()
