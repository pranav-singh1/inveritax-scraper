from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional, List
import re

from .models import NormalizedTaxRecord, Installment


_money_re = re.compile(r"[-+]?\$?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?|[0-9]+(?:\.[0-9]+)?)")


def _parse_money(val: Any) -> Optional[float]:
    if val is None:
        return None
    s = str(val).strip()
    m = _money_re.search(s)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except Exception:
        return None


def normalize_raw(county: str, parcel_number: str, raw: Dict[str, Any], source_url: Optional[str]) -> NormalizedTaxRecord:
    rec = NormalizedTaxRecord(county=county, parcel_number=parcel_number)
    rec.source_url = source_url
    rec.scrape_timestamp_utc = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    rec.raw = raw

    # These are intentionally heuristic, because each county labels fields differently.
    # In production you'd tighten these via per-county field_mapping.
    status = raw.get("delinquent_status") or raw.get("status") or raw.get("tax_status")
    if status:
        rec.delinquent_status = str(status).strip().lower()

    rec.delinquent_amount = _parse_money(raw.get("delinquent_amount") or raw.get("amount_delinquent") or raw.get("delinquent"))
    rec.penalties_interest = _parse_money(raw.get("penalties_interest") or raw.get("interest") or raw.get("penalty"))

    years = raw.get("delinquent_years") or raw.get("tax_years_delinquent")
    if years:
        if isinstance(years, list):
            rec.delinquent_tax_years = [str(y).strip() for y in years if str(y).strip()]
        else:
            rec.delinquent_tax_years = [y.strip() for y in re.split(r"[;,\s]+", str(years)) if y.strip()]

    rec.current_year_total_tax = _parse_money(raw.get("current_year_total_tax") or raw.get("current_year_tax") or raw.get("total_tax"))

    # Installments
    installments: List[Installment] = []
    for k in ["first_half_amount", "second_half_amount", "installment_1", "installment_2"]:
        if k in raw and raw.get(k) is not None:
            label = k.replace("_", " ")
            installments.append(Installment(label=label, amount=_parse_money(raw.get(k))))
    rec.installments = installments

    return rec
