from datetime import datetime, date
from db import supabase

# ============================================================
# HELPERS
# ============================================================


def format_datetime(dt: datetime) -> str:
    """Return a user-friendly datetime string."""
    return dt.strftime("%Y-%m-%d %H:%M")


def get_elapsed_time_from_now(dt: datetime) -> tuple[int, int]:
    """
    Return elapsed time from dt to now as (hours, minutes).
    Example: (2, 35) means '2h 35m ago'.
    """
    now = datetime.now()
    delta = now - dt

    total_minutes = int(delta.total_seconds() // 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60

    return hours, minutes


# ============================================================
# READ OPERATIONS
# ============================================================


def get_last_event(event_type: str):
    response = (
        supabase.table("events")
        .select("*")
        .eq("event_type", event_type)
        .order("event_time", desc=True)
        .limit(1)
        .execute()
    )

    events = response.data or []
    return events[0] if events else None


def get_all_events():
    response = (
        supabase.table("events").select("*").order("event_time", desc=True).execute()
    )
    return response.data or []


def get_feeding_details(event_id: int):
    response = (
        supabase.table("feeding_details").select("*").eq("event_id", event_id).execute()
    )

    details = response.data or []
    return details[0] if details else None


def get_diaper_details(event_id: int):
    response = (
        supabase.table("diaper_details").select("*").eq("event_id", event_id).execute()
    )

    details = response.data or []
    return details[0] if details else None


def get_last_feeding_or_bottle_event():
    """Fetch the most recent feeding event (breast or bottle)."""
    return get_last_event("feeding")


def get_last_diaper_event():
    """Fetch the most recent diaper event."""
    return get_last_event("diaper")


def get_today_events():
    """Fetch all events from today, ordered from newest to oldest."""
    today_start = datetime.combine(date.today(), datetime.min.time()).isoformat()

    response = (
        supabase.table("events")
        .select("*")
        .gte("event_time", today_start)
        .order("event_time", desc=True)
        .execute()
    )

    return response.data or []


# ============================================================
# WRITE OPERATIONS
# ============================================================


def create_event(
    event_type: str,
    event_time: datetime,
    notes: str | None,
):
    """
    Insert a new base event into the events table.
    Returns the created event row.
    """
    response = (
        supabase.table("events")
        .insert(
            {
                "event_type": event_type,
                "event_time": event_time.isoformat(),
                "notes": notes if notes else None,
            }
        )
        .execute()
    )

    created_events = response.data or []
    return created_events[0]


def create_feeding_details(
    event_id: int,
    breast: bool,
    bottle: bool,
    bottle_ml: int | None,
    breast_side: str | None,
):
    """Insert feeding-specific details linked to an event."""
    supabase.table("feeding_details").insert(
        {
            "event_id": event_id,
            "breast": breast,
            "bottle": bottle,
            "bottle_ml": bottle_ml if bottle else None,
            "breast_side": breast_side if breast and breast_side else None,
        }
    ).execute()


def create_diaper_details(event_id: int, diaper_type: str) -> None:
    """Insert diaper-specific details linked to an event."""
    supabase.table("diaper_details").insert(
        {
            "event_id": event_id,
            "diaper_type": diaper_type,
        }
    ).execute()
