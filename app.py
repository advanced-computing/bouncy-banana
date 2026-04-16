import streamlit as st

# Global styles and any shared config
st.set_page_config(layout="wide")  # if you have this

st.markdown(
    """
    <style>
        .main .block-container {
            padding-left: 5rem;
            padding-right: 5rem;
            max-width: 100%;
        }
    </style>
""",
    unsafe_allow_html=True,
)
