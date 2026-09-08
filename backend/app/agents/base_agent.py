"""Base class for EdgeHealth Guardian agents. Every agent implements
`handle(event) -> dict`, is registered on the shared EventBus, and is
individually testable/swappable -- this is what makes the "agent
consensus" model real rather than a marketing label."""
from __future__ import annotations
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    name: str = "base_agent"

    def __init__(self, bus):
        self.bus = bus

    @abstractmethod
    def handle(self, event: dict) -> dict:
        raise NotImplementedError
