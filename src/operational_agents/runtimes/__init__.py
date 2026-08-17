
"""Capa de runtimes: el agente declara la misión, el runtime la ejecuta."""

from __future__ import annotations

from .base import (
    BLOCKED,
    COMPLETED,
    FAILED,
    NOT_EXECUTED,
    AgentRuntime,
    Detection,
    ExecutionResult,
    Preparation,
    RuntimeCapabilities,
    RuntimeDescriptor,
)
from .claude import ClaudeCodeRuntime
from .manual import ManualRuntime
from .registry import RuntimeRegistry, default_registry

__all__ = [
    "BLOCKED",
    "COMPLETED",
    "FAILED",
    "NOT_EXECUTED",
    "AgentRuntime",
    "ClaudeCodeRuntime",
    "Detection",
    "ExecutionResult",
    "ManualRuntime",
    "Preparation",
    "RuntimeCapabilities",
    "RuntimeDescriptor",
    "RuntimeRegistry",
    "default_registry",
]
