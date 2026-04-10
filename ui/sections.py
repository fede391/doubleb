import streamlit as st
from datetime import datetime

from services.events import (
    format_datetime,
    get_elapsed_time_from_now,
    get_last_feeding_or_bottle_event,
    get_last_diaper_event,
    get_today_events,
    get_all_events,
    create_event,
    create_feeding_details,
    create_diaper_details,
    get_feeding_details,
    get_diaper_details,
)

# ============================================================
# KPI HEADER
# ============================================================


def render_kpi_header():
    """Render the top KPI area."""
    try:
        last_feeding = get_last_feeding_or_bottle_event()
        last_diaper = get_last_diaper_event()
        today_events = get_today_events()

        feeding_text = "No data"
        diaper_text = "No data"

        if last_feeding:
            dt = datetime.fromisoformat(last_feeding["event_time"])
            hours, minutes = get_elapsed_time_from_now(dt)
            feeding_text = f"{hours}h {minutes}m ago"

        if last_diaper:
            dt = datetime.fromisoformat(last_diaper["event_time"])
            hours, minutes = get_elapsed_time_from_now(dt)
            diaper_text = f"{hours}h {minutes}m ago"

        breast_count = 0
        bottle_count = 0
        diaper_count = 0

        for event in today_events:
            if event["event_type"] == "feeding":
                details = get_feeding_details(event["id"])
                if details:
                    if details["breast"]:
                        breast_count += 1
                    if details["bottle"]:
                        bottle_count += 1

            elif event["event_type"] == "diaper":
                diaper_count += 1

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Last feeding/bottle", feeding_text)

        with col2:
            st.metric("Last diaper", diaper_text)

        with col3:
            st.metric(
                "Today",
                f"Breast: {breast_count} | Bottle: {bottle_count} | Diapers: {diaper_count}",
            )

    except Exception as e:
        st.error(f"Error loading KPIs: {e}")


# ============================================================
# QUICK LOG
# ============================================================


def initialize_quick_log_state():
    """Initialize session state for quick log button selection."""
    if "selected_feeding" not in st.session_state:
        st.session_state.selected_feeding = False

    if "selected_bottle" not in st.session_state:
        st.session_state.selected_bottle = False

    if "selected_diaper" not in st.session_state:
        st.session_state.selected_diaper = False


def reset_quick_log_state():
    """Reset all quick log selections."""
    st.session_state.selected_feeding = False
    st.session_state.selected_bottle = False
    st.session_state.selected_diaper = False


def render_quick_log():
    """Render the quick mobile-friendly logging area."""
    st.header("Quick log")

    initialize_quick_log_state()

    col1, col2, col3 = st.columns(3)

    with col1:
        feeding_label = "✅ Feeding" if st.session_state.selected_feeding else "Feeding"
        if st.button(feeding_label, use_container_width=True, key="btn_feeding"):
            st.session_state.selected_feeding = not st.session_state.selected_feeding
            st.rerun()

    with col2:
        bottle_label = "✅ Bottle" if st.session_state.selected_bottle else "Bottle"
        if st.button(bottle_label, use_container_width=True, key="btn_bottle"):
            st.session_state.selected_bottle = not st.session_state.selected_bottle
            st.rerun()

    with col3:
        diaper_label = "✅ Diaper" if st.session_state.selected_diaper else "Diaper"
        if st.button(diaper_label, use_container_width=True, key="btn_diaper"):
            st.session_state.selected_diaper = not st.session_state.selected_diaper
            st.rerun()

    st.caption("Defaults: Feeding = 30 min, Bottle = 60 ml, Diaper = mixed")

    selected_actions = []
    if st.session_state.selected_feeding:
        selected_actions.append("feeding")
    if st.session_state.selected_bottle:
        selected_actions.append("bottle")
    if st.session_state.selected_diaper:
        selected_actions.append("diaper")

    if selected_actions:
        st.success(f"Selected: {', '.join(selected_actions)}")
    else:
        st.write("Selected: none")

    if st.button("Confirm now", use_container_width=True, key="btn_confirm_now"):
        if not selected_actions:
            st.warning("Please select at least one action.")
            return

        now = datetime.now()

        try:
            if st.session_state.selected_feeding:
                event = create_event(
                    event_type="feeding",
                    event_time=now,
                    notes="30 min",
                )
                create_feeding_details(
                    event_id=event["id"],
                    breast=True,
                    bottle=False,
                    bottle_ml=None,
                    breast_side=None,
                )

            if st.session_state.selected_bottle:
                event = create_event(
                    event_type="feeding",
                    event_time=now,
                    notes=None,
                )
                create_feeding_details(
                    event_id=event["id"],
                    breast=False,
                    bottle=True,
                    bottle_ml=60,
                    breast_side=None,
                )

            if st.session_state.selected_diaper:
                event = create_event(
                    event_type="diaper",
                    event_time=now,
                    notes=None,
                )
                create_diaper_details(
                    event_id=event["id"],
                    diaper_type="mixed",
                )

            reset_quick_log_state()
            st.success("Event(s) saved successfully!")
            st.rerun()

        except Exception as e:
            st.error(f"Error saving quick event(s): {e}")


# ============================================================
# TIMELINE
# ============================================================


def render_event_timeline():
    """Render the event timeline."""
    st.header("Event timeline")

    try:
        events = get_all_events()

        if not events:
            st.info("No events yet")
            return

        for event in events:
            event_time = datetime.fromisoformat(event["event_time"])
            formatted_time = format_datetime(event_time)

            with st.expander(f"{event['event_type'].capitalize()} - {formatted_time}"):
                if event["notes"]:
                    st.write(f"**Notes:** {event['notes']}")

                if event["event_type"] == "feeding":
                    details = get_feeding_details(event["id"])
                    if details:
                        if details["breast"]:
                            st.write("**Type:** Breast")
                        elif details["bottle"]:
                            st.write("**Type:** Bottle")
                        else:
                            st.write("**Type:** Feeding")

                        if details["bottle"]:
                            st.write(f"**Bottle amount (ml):** {details['bottle_ml']}")

                elif event["event_type"] == "diaper":
                    details = get_diaper_details(event["id"])
                    if details:
                        st.write(f"**Type:** {details['diaper_type']}")

    except Exception as e:
        st.error(f"Error loading events: {e}")
