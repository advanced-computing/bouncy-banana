import streamlit as st

main_page = st.Page("pages/1_Project_Overview.py", title="Main Page")
page_2 = st.Page("pages/1_NYC_Unemployment.py", title="NYC Unemployment")

pg = st.navigation([main_page, page_2])
pg.run()
