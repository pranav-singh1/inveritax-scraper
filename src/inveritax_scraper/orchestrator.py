from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Dict, List, Tuple

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

from .models import ParcelInput, NormalizedTaxRecord
from .engine import ScrapeEngine
from .config import CountyConfig
from .normalizer import normalize_raw


console = Console()


async def run_scrape(
    *,
    parcels: List[ParcelInput],
    county_configs: Dict[str, CountyConfig],
    engine: ScrapeEngine,
    max_concurrency: int = 5,
) -> List[NormalizedTaxRecord]:
    # group by county
    groups: Dict[str, List[ParcelInput]] = defaultdict(list)
    for p in parcels:
        groups[p.county.lower()].append(p)

    sem = asyncio.Semaphore(max_concurrency)
    out: List[NormalizedTaxRecord] = []

    async def _one(parcel: ParcelInput) -> None:
        async with sem:
            cfg = county_configs.get(parcel.county.lower())
            if not cfg:
                rec = NormalizedTaxRecord(county=parcel.county, parcel_number=parcel.parcel_number, errors=[f"No county config for {parcel.county}"])
                out.append(rec)
                return
            res = await engine.fetch(base_url=cfg.base_url, cfg=cfg.model_dump(), parcel=parcel)
            if not res.ok:
                rec = NormalizedTaxRecord(county=parcel.county, parcel_number=parcel.parcel_number, source_url=res.source_url, errors=[res.error or "Unknown error"])
                out.append(rec)
                return
            rec = normalize_raw(parcel.county, parcel.parcel_number, res.data, res.source_url)
            out.append(rec)

    tasks = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        total = len(parcels)
        t = progress.add_task("Scraping parcels", total=total)
        for parcel in parcels:
            async def _wrapped(p=parcel):
                await _one(p)
                progress.advance(t, 1)
            tasks.append(asyncio.create_task(_wrapped()))
        await asyncio.gather(*tasks)

    return out
