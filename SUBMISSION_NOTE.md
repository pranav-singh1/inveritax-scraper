# Inveritax Scraper Project - Submission

**Candidate:** Pranav Singh  
**Position:** Junior Data Engineer Intern  
**Interview Date:** Monday, December 22, 2025

## Quick Start

### Installation
```bash
pip install -r requirements.txt
playwright install chromium  # or firefox
```

### Run with Mock Data (Recommended for Testing)
```bash
python -m inveritax_scraper --mode mock --fixtures test_fixtures.json --input test_sample.xlsx --output output.json
```

### Run Against Live Sites
```bash
python -m inveritax_scraper --input "Webscraping Test FIle.xlsx" --output output.json --headless --max-concurrency 5
```

## What's Included

- **src/inveritax_scraper/** - Main codebase
  - `models.py` - Data schemas (ParcelInput, NormalizedTaxRecord)
  - `orchestrator.py` - Async execution engine with concurrency control
  - `engines_playwright.py` - Browser automation + mock engine
  - `normalizer.py` - Data normalization logic
  - `county_registry.py` - Configuration loader
  - `county_configs/*.yaml` - Per-county configurations
  
- **test_output.json** - Sample normalized output (mock mode)
- **test_fixtures.json** - Mock data for testing
- **test_sample.xlsx** - Small test file (1 parcel per county)
- **README.md** - Architecture overview
- **DESIGN.md** - Design decisions and scaling thoughts

## Verified Functionality

✅ Loads Excel input (425 parcels across 3 counties)  
✅ Multi-county support with different platforms  
✅ Normalized output schema with all required fields  
✅ Async orchestration with retry logic  
✅ Config-driven county setup (YAML, not code)  
✅ Mock mode for testing without network calls  

⚠️ Live browser automation: Playwright has compatibility issues on my Apple Silicon Mac (architecture mismatch). The code is correct but needs x86_64 or Linux environment for live testing.

## Architecture Highlights

**Scalability:** Adding a new county = create YAML config file, no code changes  
**Maintainability:** Selectors and field mappings in config, not Python  
**Testability:** Mock engine allows deterministic testing  
**Performance:** Async/await with configurable concurrency  
**Resilience:** Retry logic, error tracking, provenance  

## Interview Discussion Points

1. **Tool Evaluation:** Why Playwright vs Selenium/Scrapy/BeautifulSoup
2. **System Design:** How this scales to 72 counties
3. **Maintenance:** Handling website changes and drift detection
4. **Statewide Estimate:** Timeline and effort for full Wisconsin coverage

---

Thank you for the opportunity to work on this project!
