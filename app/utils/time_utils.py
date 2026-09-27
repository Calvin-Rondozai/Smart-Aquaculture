from datetime import datetime, timedelta


def parse_iso_timestamp(value):
    """Parses an ISO-8601 timestamp string. Returns None if invalid/missing."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except (ValueError, AttributeError):
        return None


def range_start_for(period):
    """Maps a UI time-range key (24h/7d/30d) to a start datetime."""
    now = datetime.utcnow()
    mapping = {
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
    }
    delta = mapping.get(period, timedelta(hours=24))
    return now - delta


def resolve_range(period, start=None, end=None):
    """Resolves a UI time-range selection (24h/7d/30d, or 'custom' with
    explicit ISO start/end query params) to a (start, end) datetime pair."""
    if period == "custom" and start:
        start_dt = parse_iso_timestamp(start) or range_start_for("24h")
        end_dt = parse_iso_timestamp(end) or datetime.utcnow()
        return start_dt, end_dt
    return range_start_for(period), datetime.utcnow()


def humanize_since(dt):
    if dt is None:
        return "Never"
    delta = datetime.utcnow() - dt
    seconds = int(delta.total_seconds())
    if seconds < 0:
        seconds = 0
    if seconds < 60:
        return "Just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    days = hours // 24
    return f"{days} day{'s' if days != 1 else ''} ago"
