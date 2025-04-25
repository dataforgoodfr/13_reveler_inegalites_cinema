import dateparser

def parse_release_date(date_str):
    try:
        parsed = dateparser.parse(date_str, languages=["fr"])
        return parsed.date() if parsed else None
    except Exception:
        return None

def parse_duration(duration_str):
    try:
        if not duration_str or not duration_str.strip():
            return None

        hours, minutes = 0, 0
        if 'h' in duration_str:
            parts = duration_str.split('h')
            hours = int(parts[0].strip())
            minutes = int(parts[1].replace('min', '').strip()) if 'min' in parts[1] else 0
        elif 'min' in duration_str:
            minutes = int(duration_str.replace('min', '').strip())

        total = hours * 60 + minutes
        return total if total > 0 else None

    except Exception:
        return None