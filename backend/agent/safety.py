import logging
from typing import Tuple

from backend.config import BLOCKED_KEYWORDS

logger = logging.getLogger(__name__)

# Patterns that are destructive or commonly used for abuse. These are refused
# regardless of context. NOVA is a personal productivity assistant, not an
# intrusion tool.
DANGEROUS_PATTERNS = [
    "rm -rf",
    "dd if=",
    "mkfs",
    "fdisk",
    ":(){",          # fork bomb
    "format c:",
    "del /f /s /q",
    "shutdown",
    "reg delete",
    "> /dev/sd",
]


def is_command_safe(command: str) -> Tuple[bool, str]:
    """Return ``(safe, reason)`` for a shell command.

    Blocks known-dangerous patterns and the configured blocked keywords so
    the assistant never runs destructive or malicious commands.
    """
    lowered = command.lower()

    for keyword in BLOCKED_KEYWORDS:
        if keyword.lower() in lowered:
            return False, f"blocked keyword: {keyword}"

    for pattern in DANGEROUS_PATTERNS:
        if pattern.lower() in lowered:
            return False, f"dangerous pattern: {pattern}"

    return True, ""
