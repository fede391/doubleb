import streamlit as st
from ui.sections import (
    render_kpi_header,
    render_quick_log,
    render_event_timeline,
)

st.set_page_config(page_title="DoubleB", page_icon="👶")

st.title("DoubleB 👶")

render_kpi_header()
render_quick_log()
render_event_timeline()
