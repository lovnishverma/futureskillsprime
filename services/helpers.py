import re
from datetime import datetime, timezone, timedelta

# Indian Standard Time (IST = UTC+05:30)
try:
    from zoneinfo import ZoneInfo
    IST = ZoneInfo("Asia/Kolkata")
except Exception:
    IST = timezone(timedelta(hours=5, minutes=30), name="IST")

def get_ist_now():
    """Get current datetime in Indian Standard Time (Asia/Kolkata)."""
    try:
        return datetime.now(IST)
    except Exception:
        return datetime.now(timezone(timedelta(hours=5, minutes=30)))

def get_ist_date():
    """Get current date in Indian Standard Time."""
    return get_ist_now().date()

def fmt_date(val):
    """Convert YYYY-MM-DD → DD-MM-YYYY."""
    if val and re.match(r"^\d{4}-\d{2}-\d{2}$", val):
        try:
            return datetime.strptime(val, "%Y-%m-%d").strftime("%d-%m-%Y")
        except Exception:
            pass
    return val or ""

def is_batch_active(end_str):
    """Check if a batch's end date has not passed yet in IST (end_date >= ist_today)."""
    if not end_str:
        return False
    try:
        end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
        return end_date >= get_ist_date()
    except Exception:
        return False

def get_batch_status_badge(start_str, end_str):
    """
    Returns a status dict:
    - label: 'Starting Soon' / 'Starts in X Days' / 'Enrollment Open' / 'Passed'
    - type: 'starting_soon' / 'open' / 'passed'
    """
    if not start_str or not end_str:
        return None
    try:
        s = datetime.strptime(start_str, "%Y-%m-%d").date()
        e = datetime.strptime(end_str, "%Y-%m-%d").date()
        today = get_ist_date()
        
        if e < today:
            return {"label": "Passed", "type": "passed"}
        elif s > today:
            days_left = (s - today).days
            if days_left == 1:
                return {"label": "Starts Tomorrow", "type": "starting_soon"}
            elif days_left <= 7:
                return {"label": f"Starts in {days_left} Days", "type": "starting_soon"}
            else:
                return {"label": "Starting Soon", "type": "starting_soon"}
        else:
            return {"label": "Enrollment Open", "type": "open"}
    except Exception:
        return None

def get_ordinal(n):
    return str(n) + ('th' if 11 <= n % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th'))

def fmt_course_dates(start_str, end_str):
    if not start_str or not end_str:
        return ""
    try:
        s = datetime.strptime(start_str, "%Y-%m-%d")
        e = datetime.strptime(end_str, "%Y-%m-%d")
        s_fmt = f"{get_ordinal(s.day)} {s.strftime('%B')}, {s.year}"
        e_fmt = f"{get_ordinal(e.day)} {e.strftime('%B')}, {e.year}"
        return f"{s_fmt} - {e_fmt}"
    except Exception:
        return ""

def _course_name(track, level):
    track = (track or "").upper()
    level = (level or "").capitalize()
    mapping = {
        "ARVR_Basic": "Government Officials Training (GOT) Program in Augmented Reality (AR) & Virtual Reality (VR) – Basic Level",
        "ARVR_Advanced": "Government Officials Training (GOT) Program in Augmented Reality (AR) & Virtual Reality (VR) – Advanced Level",
        "ARVR_Bootcamp": "Bootcamp in Augmented Reality (AR) & Virtual Reality (VR)",
        "BDDS_Basic": "Government Officials Training (GOT) Program in Big Data & Data Science (BD&DS) – Basic Level",
        "BDDS_Advanced": "Government Officials Training (GOT) Program in Big Data & Data Science (BD&DS) – Advanced Level",
        "BDDS_Bootcamp": "Bootcamp in Big Data & Data Science (BD&DS)"
    }
    return mapping.get(f"{track}_{level}", "Unknown Course")

def _technology(track):
    track = (track or "").upper()
    if track == "ARVR": return "Augmented Reality (AR) & Virtual Reality (VR)"
    if track == "BDDS": return "Big Data & Data Science (BD&DS)"
    return track
