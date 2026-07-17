"""Shared utilities used across SAM backend modules."""

import asyncio
import functools
from datetime import datetime
from typing import Any, Callable, Iterable


async def run_blocking(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Run a blocking callable in the default executor without blocking the loop."""
    loop = asyncio.get_event_loop()
    if args or kwargs:
        func = functools.partial(func, *args, **kwargs)
    return await loop.run_in_executor(None, func)


def generate_id(prefix: str) -> str:
    """Generate a timestamp-based identifier with the given prefix."""
    return f"{prefix}_{datetime.now().timestamp()}"


def contains_any(text: str, keywords: Iterable[str]) -> bool:
    """Return True if any keyword appears in text (case-insensitive)."""
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)
