# Inveritax Candidate Project: Scalable Multi-County Scraping Framework

This is a **framework-first** implementation that matches the exercise goal: demonstrate how to scale across counties by separating:
1) a reusable scraping engine + orchestrator, from
2) per-county configuration (URLs, search workflow, field mappings).

It reads the provided Excel input (parcel records per county), visits the correct county site, and emits **normalized JSON** per parcel.

## What you can run locally

### 1) Install deps
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

### 2) Run (live mode, browser automation)
```bash
python -m inveritax_scraper run --input "Webscraping Test FIle.xlsx" --output output.json --headless --max-concurrency 5
```

### 3) Run (mock mode, no network)
```bash
python -m inveritax_scraper run --mode mock --fixtures tests/fixtures/fixtures.json --input "Webscraping Test FIle.xlsx"
```

## Where to edit county behavior

County configuration files live in:
- `src/inveritax_scraper/county_configs/*.yaml`

Each county config contains placeholders for Playwright selectors:
- `search_input_selector`
- `search_button_selector`
- optional `result_row_selector` + `details_link_selector`
- `extract` mapping of field -> selector

The intent is: **when a county site changes, update YAML, not Python.**

## Output schema

The normalized record matches the minimum data requested:
- delinquent status/amount/years/installments/penalty+interest
- current-year total tax
- installment breakdown (first/second half)
- due dates (if present on the site)

Implementation note: normalization is intentionally heuristic in `normalizer.py` because each county labels fields differently. In production you would tighten it by adding per-county `field_mapping` rules.

## Why this is structured this way

- Multi-county support via a **county registry** (`county_registry.py`)
- Parallel execution and throttling via `asyncio` in `orchestrator.py`
- Swappable engines:
  - `PlaywrightEngine` for real sites
  - `MockEngine` for deterministic tests / no-network environments

## Next steps you can mention in the interview

- Add a lightweight per-county “mapping DSL” (regex/label matching) to reduce selector fragility.
- Add retries + screenshot capture on failures for debugging.
- Add result caching keyed by (county, parcel, run_date) to avoid re-scraping.
- Add monitoring: success rate per county, drift detection, alerting.

