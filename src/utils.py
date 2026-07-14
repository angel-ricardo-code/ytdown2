import re
import string


def sanitize_filename(s: str, max_length: int = 200) -> str:
    """Make a filesystem-safe filename. Keep it simple and cross-platform."""
    # Replace path separators and control chars
    s = s.replace("/", "-").replace("\\", "-")
    # Remove characters that are problematic on Windows
    valid = "-_.() %s%s" % (string.ascii_letters, string.digits)
    cleaned = "".join(c for c in s if c in valid)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rstrip()
    return cleaned or "video"
