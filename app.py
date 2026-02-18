import pandas as pd
import requests
import streamlit as st

main_page = st.Page("main_page.py", title="Main Page")
page_2 = st.Page("page_2.py", title="Page 2")

pg = st.navigation([main_page, page_2])
pg.run()
