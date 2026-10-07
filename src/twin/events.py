from __future__ import annotations

from collections.abc import Callable
from .state import TwinEvent


class EventBus:
    def __init__(self) -> None:
        self.events: list[TwinEvent] = []
        self._subscribers: list[Callable[[TwinEvent], None]] = []

    def subscribe(self, callback: Callable[[TwinEvent], None]) -> None:
        self._subscribers.append(callback)

    def publish(self, event: TwinEvent) -> None:
        self.events.append(event)
        self.events = self.events[-500:]
        for callback in self._subscribers:
            callback(event)

