from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from .models import ParcelInput


class ScrapeResult:
    def __init__(self, ok: bool, data: Optional[Dict[str, Any]] = None, source_url: Optional[str] = None, error: Optional[str] = None):
        self.ok = ok
        self.data = data or {}
        self.source_url = source_url
        self.error = error


class ScrapeEngine(ABC):
    @abstractmethod
    async def start(self) -> None:
        ...

    @abstractmethod
    async def stop(self) -> None:
        ...

    @abstractmethod
    async def fetch(self, *, base_url: str, cfg: Dict[str, Any], parcel: ParcelInput) -> ScrapeResult:
        ...
