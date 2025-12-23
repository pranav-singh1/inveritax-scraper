from __future__ import annotations

from pathlib import Path
from typing import List
import pandas as pd

from .models import ParcelInput


SHEET_HINTS = ["Records"]


def load_parcels_from_excel(xlsx_path: Path) -> List[ParcelInput]:
    xl = pd.ExcelFile(xlsx_path)
    parcels: List[ParcelInput] = []
    for sheet in xl.sheet_names:
        if any(h in sheet for h in SHEET_HINTS):
            df = pd.read_excel(xlsx_path, sheet_name=sheet)
            # expected columns: County, Parcel Number, Owner Name, Property Address
            for _, row in df.iterrows():
                county = str(row.get("County", "")).strip()
                parcel = str(row.get("Parcel Number", "")).strip()
                if not county or not parcel or parcel.lower() == "nan":
                    continue
                parcels.append(
                    ParcelInput(
                        county=county,
                        parcel_number=parcel,
                        owner_name=(None if pd.isna(row.get("Owner Name")) else str(row.get("Owner Name")).strip()),
                        property_address=(None if pd.isna(row.get("Property Address")) else str(row.get("Property Address")).strip()),
                    )
                )
    return parcels
