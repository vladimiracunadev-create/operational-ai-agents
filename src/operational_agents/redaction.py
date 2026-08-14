
from __future__ import annotations

import re

PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*[^\s,;]+"),
    re.compile(r"(?i)authorization:\s*bearer\s+[^\s]+"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
]


def redact(text: str) -> str:
    result = text
    for pattern in PATTERNS:
        result = pattern.sub("[REDACTED]", result)
    return result
