import streamlit as st

st.set_page_config(page_title="DoubleB", page_icon="👶")

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

from ui.sections import (
    render_kpi_header,
    render_quick_log,
    render_event_timeline,
)

st.title("DoubleB 👶")

render_kpi_header()
render_quick_log()
render_event_timeline()
