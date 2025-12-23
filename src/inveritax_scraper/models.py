from __future__ import annotations

from datetime import date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ParcelInput(BaseModel):
    county: str = Field(..., description="County name (e.g., Brown)")
    parcel_number: str = Field(..., description="Parcel ID / Tax Key Number")
    owner_name: Optional[str] = None
    property_address: Optional[str] = None


class Installment(BaseModel):
    label: str
    amount: Optional[float] = None
    due_date: Optional[date] = None


class NormalizedTaxRecord(BaseModel):
    county: str
    parcel_number: str

    # Delinquent tax data
    delinquent_status: Optional[str] = None  # e.g., delinquent, paid, unknown
    delinquent_amount: Optional[float] = None
    delinquent_tax_years: List[str] = Field(default_factory=list)
    delinquent_installments: List[str] = Field(default_factory=list)
    penalties_interest: Optional[float] = None

    # Escrow / current-year amounts
    current_year_total_tax: Optional[float] = None
    installments: List[Installment] = Field(default_factory=list)

    # Provenance + diagnostics
    source_url: Optional[str] = None
    scrape_timestamp_utc: Optional[str] = None
    raw: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
