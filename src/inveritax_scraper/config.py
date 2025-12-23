from __future__ import annotations

from typing import Literal, Optional, Dict, Any, List
from pydantic import BaseModel, Field


SearchMode = Literal["parcel_number", "address", "owner_name"]


class CountyConfig(BaseModel):
    county: str
    platform: str  # e.g., Ascent, GCS, LandNav
    base_url: str

    # which inputs this county supports
    supported_search_modes: List[SearchMode] = Field(default_factory=lambda: ["parcel_number"])

    # selectors / actions are intentionally high-level so they can be tweaked without code changes
    selectors: Dict[str, Any] = Field(default_factory=dict)

    # mapping from page fields -> normalized keys
    field_mapping: Dict[str, str] = Field(default_factory=dict)

    # optional notes for maintainers
    notes: Optional[str] = None
