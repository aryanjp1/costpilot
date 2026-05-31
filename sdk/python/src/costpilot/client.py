import logging
import threading
import time

from .models import Event
from .queue import EventQueue

logger = logging.getLogger("costpilot")


class CostPilotClient:
    """Buffers events and ships them to the CostPilot backend in batches.

    The client owns a background thread that flushes on a fixed interval, plus
    an immediate flush whenever the queue fills up. Nothing here is allowed to
    bubble an exception into the host application.
    """

    def __init__(
        self,
        api_key: str,
        endpoint: str,
        default_tags: dict[str, str] | None = None,
        flush_interval: float = 5.0,
        batch_size: int = 50,
    ):
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        self.default_tags = default_tags or {}
        self._flush_interval = flush_interval
        self._batch_size = batch_size
        self._queue = EventQueue(batch_size=batch_size)
        self._running = True
        self._flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self._flush_thread.start()

    def track(self, event: Event) -> None:
        try:
            should_flush = self._queue.add(event)
            if should_flush:
                self._flush_now()
        except Exception:
            pass

    def flush(self) -> None:
        """Drain everything currently queued. Safe to call from host code."""
        try:
            while len(self._queue):
                self._flush_now()
        except Exception:
            pass

    def shutdown(self) -> None:
        self._running = False
        self.flush()

    def _flush_loop(self) -> None:
        while self._running:
            time.sleep(self._flush_interval)
            try:
                self._flush_now()
            except Exception:
                pass

    def _flush_now(self) -> None:
        batch = self._queue.drain(self._batch_size)
        if not batch:
            return
        threading.Thread(
            target=self._send_batch, args=(batch,), daemon=True
        ).start()

    def _send_batch(self, batch: list[Event]) -> None:
        try:
            import httpx

            httpx.post(
                f"{self.endpoint}/api/ingest",
                json={"events": [e.to_dict() for e in batch]},
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=5.0,
            )
        except Exception as exc:
            logger.debug("dropped %d events: %s", len(batch), exc)
