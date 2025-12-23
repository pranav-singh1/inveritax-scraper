from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

from .county_registry import load_county_configs
from .input_loader import load_parcels_from_excel
from .engines_playwright import PlaywrightEngine, MockEngine
from .orchestrator import run_scrape


app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def run(
    input_xlsx: Path = typer.Option(..., "--input", exists=True, help="Input Excel file (provided by Inveritax)"),
    output_json: Path = typer.Option(Path("output.json"), "--output", help="Where to write normalized JSON"),
    headless: bool = typer.Option(True, "--headless/--headed", help="Run browser headless"),
    max_concurrency: int = typer.Option(5, "--max-concurrency", min=1, max=20),
    mode: str = typer.Option("live", "--mode", help="live | mock"),
    fixtures_json: Optional[Path] = typer.Option(None, "--fixtures", help="Mock fixtures json (only for --mode mock)"),
):
    config_dir = Path(__file__).parent / "county_configs"
    county_configs = load_county_configs(config_dir)

    parcels = load_parcels_from_excel(input_xlsx)
    console.print(f"Loaded {len(parcels)} parcels from {input_xlsx}")

    async def _runner():
        if mode == "mock":
            if not fixtures_json or not fixtures_json.exists():
                raise typer.BadParameter("mock mode requires --fixtures pointing to a fixtures json file")
            fixtures = json.loads(fixtures_json.read_text())
            engine = MockEngine(fixtures=fixtures)
        else:
            engine = PlaywrightEngine(headless=headless)

        await engine.start()
        try:
            records = await run_scrape(parcels=parcels, county_configs=county_configs, engine=engine, max_concurrency=max_concurrency)
        finally:
            await engine.stop()

        output_json.write_text(json.dumps([r.model_dump() for r in records], indent=2, default=str))
        console.print(f"Wrote {len(records)} records to {output_json}")

    asyncio.run(_runner())


if __name__ == "__main__":
    app()
