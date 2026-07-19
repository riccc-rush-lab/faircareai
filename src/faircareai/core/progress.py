"""Lightweight progress reporting for long-running audits."""

from __future__ import annotations

import sys
import time
from collections.abc import Callable
from typing import TextIO


class ProgressReporter:
    """Emit stable, notebook-visible audit progress lines."""

    def __init__(
        self,
        *,
        enabled: bool = True,
        stream: TextIO | None = None,
        clock: Callable[[], float] = time.perf_counter,
    ) -> None:
        self.enabled = enabled
        self.stream = stream or sys.stdout
        self._clock = clock
        self._started_at = clock()

    def stage(self, current: int, total: int, message: str) -> None:
        """Print one numbered stage line."""
        if self.enabled:
            print(f"[{current}/{total}] {message}", file=self.stream, flush=True)

    def complete(self) -> None:
        """Print total elapsed wall-clock time."""
        if self.enabled:
            elapsed = self._clock() - self._started_at
            print(f"Audit complete in {elapsed:.2f}s", file=self.stream, flush=True)
