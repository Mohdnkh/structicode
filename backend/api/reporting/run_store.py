"""Bounded, thread-safe, process-local storage for P7 analysis snapshots."""

from __future__ import annotations

from collections import OrderedDict
from os import getenv
from threading import RLock
from typing import Protocol

from .models import AnalysisRunRecord


class AnalysisRunStore(Protocol):
    def put(self, record: AnalysisRunRecord) -> None: ...
    def get(self, run_id: str) -> AnalysisRunRecord | None: ...


class InMemoryAnalysisRunStore:
    """A deterministic FIFO store; records are lost when the process restarts."""

    def __init__(self, max_records: int = 100):
        if max_records < 1:
            raise ValueError("max_records must be at least one")
        self.max_records = max_records
        self._records: OrderedDict[str, AnalysisRunRecord] = OrderedDict()
        self._lock = RLock()

    def put(self, record: AnalysisRunRecord) -> None:
        with self._lock:
            self._records[record.run_id] = record.model_copy(deep=True)
            self._records.move_to_end(record.run_id)
            while len(self._records) > self.max_records:
                self._records.popitem(last=False)

    def get(self, run_id: str) -> AnalysisRunRecord | None:
        with self._lock:
            record = self._records.get(run_id)
            return record.model_copy(deep=True) if record is not None else None


def _configured_limit() -> int:
    try:
        return max(1, int(getenv("STRUCTICODE_ANALYSIS_RUN_LIMIT", "100")))
    except ValueError:
        return 100


RUN_STORE = InMemoryAnalysisRunStore(_configured_limit())
