"""Pluggable "brain" (LLM backend) abstraction for NOVA.

Each brain wraps a single LLM provider behind a common interface so new
providers can be added without touching the rest of the system. The
``BrainRouter`` selects among registered brains and fails over automatically.
"""

from backend.brains.base import Brain
from backend.brains.router import BrainRouter
from backend.brains.adapters import GeminiBrain, GroqBrain

__all__ = ["Brain", "BrainRouter", "GeminiBrain", "GroqBrain"]
