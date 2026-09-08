"""Minimal local pub/sub event bus. Runs in-process on the edge hub --
no network hop between agents, which is why the multi-agent
consensus check can complete in milliseconds."""
from __future__ import annotations
from collections import defaultdict
from typing import Callable


class EventBus:
    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)
        self.log: list[dict] = []

    def subscribe(self, event_type: str, handler: Callable):
        self._subscribers[event_type].append(handler)

    def publish(self, event_type: str, payload: dict):
        self.log.append({"type": event_type, "payload": payload})
        results = []
        for handler in self._subscribers[event_type]:
            results.append(handler(payload))
        return results
