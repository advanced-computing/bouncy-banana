import streamlit as st

main_page = st.Page("Project_Overview.py", title="Main Page")
page_2 = st.Page("pages/1_NYC_Unemployment.py", title="NYC Unemployment")
page_3 = st.Page("pages/2_NYC_Evictions.py", title="NYC Evictions")

pg = st.navigation([main_page, page_2, page_3])
pg.run()
