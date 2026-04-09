import streamlit as st
from datetime import datetime

st.set_page_config(page_title="DoubeB", page_icon="👶")

st.title("DoubeB 👶")
st.subheader("Track your baby events")

# --- Form per inserire evento ---
st.header("Add new event")

event_type = st.selectbox(
    "Event type",
    ["Feeding", "Diaper"]
)

notes = st.text_input("Notes (optional)")

if st.button("Save event"):
    event = {
        "type": event_type,
        "notes": notes,
        "timestamp": datetime.now()
    }

    st.success("Event saved!")
    st.write(event)