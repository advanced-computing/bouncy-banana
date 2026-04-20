import streamlit as st

st.set_page_config(
    page_title="Project Dashboard",
    page_icon="🗽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500&display=swap');
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

  .wip-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 20px;
    text-align: center;
  }
  .wip-badge {
    display: inline-block;
    background: #fef9c3;
    color: #854d0e;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 6px 16px;
    border-radius: 999px;
    border: 1px solid #fde68a;
    margin-bottom: 24px;
  }
  .wip-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.8rem;
    color: #1a1a2e;
    margin: 0 0 16px;
    line-height: 1.15;
  }
  .wip-subtitle {
    font-size: 1rem;
    color: #6b7280;
    max-width: 480px;
    line-height: 1.7;
    margin: 0 auto 40px;
  }
  .wip-divider {
    width: 48px;
    height: 3px;
    background: #3b82f6;
    border-radius: 999px;
    margin: 0 auto 40px;
  }
  .wip-footer {
    font-size: 0.8rem;
    color: #9ca3af;
    margin-top: 48px;
  }
</style>

<div class="wip-container">
  <div class="wip-badge">🚧 &nbsp; Under Construction</div>
  <h1 class="wip-title">NYC Unemployment Dashboard</h1>
  <div class="wip-divider"></div>
  <p class="wip-subtitle">
    This dashboard is currently in development. We're building an interactive
    exploration of how unemployment rates relate to lifestyle outcomes
    across New York City's five boroughs.
  </p>
  <p class="wip-footer">Come back soon — something good is on the way. 🗽</p>
</div>
""",
    unsafe_allow_html=True,
)
