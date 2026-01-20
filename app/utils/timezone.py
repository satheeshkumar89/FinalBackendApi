"""
Timezone utility for converting all timestamps to Indian Standard Time (IST).
Tamil Nadu, India timezone: Asia/Kolkata (UTC+5:30)
"""

from datetime import datetime, timezone, timedelta
import pytz

# Indian Standard Time timezone
IST = pytz.timezone('Asia/Kolkata')

def get_ist_now():
    """
    Get current time in Indian Standard Time (IST).
    Use this instead of datetime.utcnow() throughout the application.
    """
    return datetime.now(IST)

def utc_to_ist(utc_datetime):
    """
    Convert UTC datetime to IST.
    
    Args:
        utc_datetime: datetime object in UTC
        
    Returns:
        datetime object in IST
    """
    if utc_datetime is None:
        return None
    
    # If datetime is naive (no timezone info), assume it's UTC
    if utc_datetime.tzinfo is None:
        utc_datetime = pytz.utc.localize(utc_datetime)
    
    # Convert to IST
    return utc_datetime.astimezone(IST)

def ist_to_utc(ist_datetime):
    """
    Convert IST datetime to UTC (for database storage if needed).
    
    Args:
        ist_datetime: datetime object in IST
        
    Returns:
        datetime object in UTC
    """
    if ist_datetime is None:
        return None
    
    # If datetime is naive, assume it's IST
    if ist_datetime.tzinfo is None:
        ist_datetime = IST.localize(ist_datetime)
    
    # Convert to UTC
    return ist_datetime.astimezone(pytz.utc)

def format_ist_datetime(dt, format_string="%d-%m-%Y %I:%M %p"):
    """
    Format datetime in IST with Indian date format.
    
    Args:
        dt: datetime object
        format_string: strftime format string
        
    Returns:
        Formatted string in IST
    """
    if dt is None:
        return None
    
    # Convert to IST if not already
    ist_dt = utc_to_ist(dt) if dt.tzinfo != IST else dt
    
    return ist_dt.strftime(format_string)
