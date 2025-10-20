# app/core/time_utils.py
from datetime import datetime, timezone

def utc_now():
    """Devuelve la hora actual con zona horaria UTC."""
    return datetime.now(timezone.utc)