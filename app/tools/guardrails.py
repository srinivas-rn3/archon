import re

# Patterns for common sensitive data. Not exhaustive, but covers the
# highest-risk, most common leaks.
PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone": re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "aws_secret_key": re.compile(r"\b[A-Za-z0-9/+=]{40}\b"),
    "ssn_like": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
}


def scan_for_pii(text: str) -> dict:
    """
    Scans text for common PII/sensitive data patterns.
    Returns a dict of {pii_type: [matches]} for anything found.
    """
    findings = {}
    for pii_type, pattern in PII_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            findings[pii_type] = matches
    return findings


def redact_pii(text: str) -> tuple[str, dict]:
    """
    Replaces any detected PII in the text with a redaction marker.
    Returns (redacted_text, findings) so the caller knows what was caught.
    """
    findings = scan_for_pii(text)
    redacted_text = text

    for pii_type, pattern in PII_PATTERNS.items():
        redacted_text = pattern.sub(f"[REDACTED_{pii_type.upper()}]", redacted_text)

    return redacted_text, findings