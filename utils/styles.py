import streamlit as st


def apply_global_styles():
    st.markdown(
        """
        <style>
            .main .block-container {
                padding-left: 2rem;
                padding-right: 2rem;
                max-width: 100%;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )
