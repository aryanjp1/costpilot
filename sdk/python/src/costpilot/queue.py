import threading

from .models import Event


class EventQueue:
    """Thread-safe buffer of events waiting to be flushed.

    Drains in batches so the client never sends one HTTP request per call.
    """

    def __init__(self, batch_size: int = 50):
        self._batch_size = batch_size
        self._events: list[Event] = []
        self._lock = threading.Lock()

    def add(self, event: Event) -> bool:
        """Append an event. Returns True when the queue is ready to flush."""
        with self._lock:
            self._events.append(event)
            return len(self._events) >= self._batch_size

    def drain(self, limit: int | None = None) -> list[Event]:
        """Pop up to ``limit`` events (defaults to one batch)."""
        size = limit or self._batch_size
        with self._lock:
            batch = self._events[:size]
            self._events = self._events[size:]
            return batch

    def __len__(self) -> int:
        with self._lock:
            return len(self._events)
