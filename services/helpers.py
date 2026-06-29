import re
from datetime import datetime

def fmt_date(val):
    """Convert YYYY-MM-DD → DD-MM-YYYY."""
    if val and re.match(r"^\d{4}-\d{2}-\d{2}$", val):
        try:
            return datetime.strptime(val, "%Y-%m-%d").strftime("%d-%m-%Y")
        except Exception:
            pass
    return val or ""

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
