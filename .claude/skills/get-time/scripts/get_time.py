#!/usr/bin/env python3
"""
Get the current local time in various formats with automatic timezone detection.
"""

from datetime import datetime
import sys
import urllib.request
import json

def get_user_timezone():
    """
    Detect user's timezone using IP geolocation.
    Falls back to UTC if detection fails.
    """
    try:
        # Use ipapi.co free API to get timezone from IP
        with urllib.request.urlopen('https://ipapi.co/json/', timeout=3) as response:
            data = json.loads(response.read().decode())
            return data.get('timezone', 'UTC')
    except:
        # Fallback to UTC if detection fails
        return 'UTC'

def get_current_time(format_type="full", timezone=None):
    """
    Get current local time in specified format.
    
    Args:
        format_type: Type of format to return
            - "full": Full datetime with timezone (default)
            - "time": Just the time (HH:MM:SS)
            - "date": Just the date (YYYY-MM-DD)
            - "datetime": Date and time without timezone
            - "iso": ISO 8601 format
            - "unix": Unix timestamp
        timezone: Specific timezone to use (auto-detected if None)
    
    Returns:
        Formatted time string
    """
    try:
        # Import zoneinfo for timezone support (Python 3.9+)
        from zoneinfo import ZoneInfo
    except ImportError:
        # Fallback for older Python versions
        try:
            from backports.zoneinfo import ZoneInfo
        except ImportError:
            # If no timezone support, just use UTC
            now = datetime.utcnow()
            tz_name = "UTC"
            formats = {
                "full": now.strftime(f"%A, %B %d, %Y at %I:%M:%S %p {tz_name}"),
                "time": now.strftime("%I:%M:%S %p"),
                "date": now.strftime("%Y-%m-%d"),
                "datetime": now.strftime("%Y-%m-%d %I:%M:%S %p"),
                "iso": now.isoformat(),
                "unix": str(int(now.timestamp()))
            }
            return formats.get(format_type, formats["full"])
    
    # Auto-detect timezone if not provided
    if timezone is None:
        timezone = get_user_timezone()
    
    # Get current time in the detected/specified timezone
    tz = ZoneInfo(timezone)
    now = datetime.now(tz)
    
    # Format the timezone abbreviation
    tz_abbr = now.strftime("%Z")
    
    formats = {
        "full": now.strftime(f"%A, %B %d, %Y at %I:%M:%S %p {tz_abbr}"),
        "time": now.strftime("%I:%M:%S %p"),
        "date": now.strftime("%Y-%m-%d"),
        "datetime": now.strftime(f"%Y-%m-%d %I:%M:%S %p {tz_abbr}"),
        "iso": now.isoformat(),
        "unix": str(int(now.timestamp()))
    }
    
    return formats.get(format_type, formats["full"])

if __name__ == "__main__":
    # Get format from command line argument, default to "full"
    format_arg = sys.argv[1] if len(sys.argv) > 1 else "full"
    
    # Optional timezone argument
    timezone_arg = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(get_current_time(format_arg, timezone_arg))
