import streamlit as st

from eviction import borough_count, eviction

eviction_data = eviction()
borough_count_clean = borough_count(eviction_data)

st.bar_chart(borough_count_clean, x="borough", y="Count")

st.title("NYC Eviction Data")
st.sidebar.markdown("Page 2")
