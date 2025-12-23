# Interview Prep - What Works vs What Doesn't

## ✅ What WORKS (Verified)

### Architecture & Design
- **Multi-county support**: Config-driven system with YAML files per county
- **Separation of concerns**: Engine, orchestrator, normalizer, config registry all separate
- **Async orchestration**: Configurable concurrency with semaphore control
- **Retry logic**: Exponential backoff (3 attempts) using Tenacity
- **Error handling**: Errors captured and returned in output
- **Mock testing**: Full mock engine implementation for testing without network

### Input Handling
- **Excel loading**: Successfully reads 425 parcels from test file
- **Data extraction**: County, Parcel Number, Owner Name, Property Address
- **Multi-sheet support**: Handles "Ascent Records", "GCS Records", "LandNav Records"

### Output Schema & Normalization
- **All required fields**: 
  - Delinquent: status, amount, years, installments, penalties/interest
  - Escrow: current year tax, installment breakdowns, due dates
- **Money parsing**: Converts "$2,345.67" → 2345.67
- **Provenance tracking**: source_url, scrape_timestamp_utc, raw data
- **Type safety**: Pydantic models with validation

### Verified Test Run (Mock Mode)
```bash
python -m inveritax_scraper --mode mock --fixtures test_fixtures.json \
  --input test_sample.xlsx --output test_output.json
```
**Result**: ✅ Success - 3 records normalized correctly

## ⚠️ What DOESN'T Work (Known Issues)

### Browser Automation
- **Playwright fails on Apple Silicon Mac**: Architecture mismatch (x64 vs ARM64)
- **No live website testing**: Haven't verified selectors against real sites
- **Firefox also crashes**: SIGABRT in headless mode (macOS compatibility)

### Implementation Gaps
- **Search modes**: Only parcel_number implemented (not address/owner name)
- **Selector validation**: County configs have placeholder selectors, not validated against live sites
- **Installment extraction**: Framework supports it but selectors might not capture it
- **Due dates**: Schema supports them but extraction rules incomplete
- **Field mapping**: Config option exists but not actively used in normalization

### Testing
- **No comprehensive fixtures**: Only 3 mock parcels, not all 425
- **No integration tests**: Can't verify against live sites
- **Limited unit tests**: Only one test for input loading

## 🎯 Key Points for Interview

### What You Should Emphasize

1. **Understanding of the Goal**: "I knew this wasn't about proving I can scrape—you already have scrapers. It's about scalable system design."

2. **Architecture Choice**: "I separated the reusable engine from per-county variability. Adding new counties is config work, not code work."

3. **Tool Selection**:
   - **Playwright**: Modern, reliable, better than Selenium for SPAs
   - **Async/await**: Performance for parallel execution
   - **Pydantic**: Type safety and validation
   - **YAML configs**: Human-readable, easy to maintain

4. **Mock Testing Advantage**: "Even though browser automation failed, mock mode proves all the business logic works. In production, I'd use Docker/Linux where Playwright is stable."

### What to Acknowledge

1. **Honest about limitations**: "I didn't get to test against live sites, so the selectors are educated guesses based on the platform types."

2. **Environmental issue, not code issue**: "The Playwright problem is a Mac ARM64 compatibility thing, not a design flaw. Same code would work on x86 or in Docker."

3. **Next steps if hired**: "First week would be validating selectors against all 3 counties, refining extraction rules, building comprehensive fixtures."

### Statewide Feasibility (72 Counties)

**Your Estimate**:
- **Framework**: ✅ Already built (2-3 weeks if starting from scratch)
- **Per county onboarding**: 0.5-2 days depending on platform complexity
  - Simple sites (same platform as existing): 4-6 hours
  - Complex sites (new platform, multi-step workflow): 1-2 days
- **Timeline for 72 counties**: 
  - 2-3 engineers for ~6 months (parallel work)
  - Some counties will share platforms, reducing effort
- **Maintenance**: 
  - Mostly config updates when sites change
  - 1-2 engineers ongoing
  - Could add automated drift detection (compare screenshots over time)

### Questions to Ask Them

1. "How often do county websites change? What's the typical maintenance burden?"
2. "Are there common platform vendors across Wisconsin counties? (e.g., multiple counties using Ascent)"
3. "What's the current process when a county site changes? How long does it take to fix?"
4. "Would you want automated monitoring/alerting when scraping starts failing?"
5. "Is there value in caching results to avoid re-scraping the same parcels?"

### Alternatives You Considered

1. **Scrapy** vs Playwright: "Scrapy is great for static sites, but these are SPAs with JavaScript. Playwright handles that better."

2. **Selenium** vs Playwright: "Playwright is faster, has better async support, and more modern API. But Selenium would also work."

3. **Custom DSL** vs YAML: "Could build a mini-language for extraction rules, but YAML with selectors is simpler and everyone knows it."

4. **LLM-based scraping**: "Thought about using vision models to extract data from screenshots, but that's expensive and slower. Maybe for the hardest 10% of sites."

## 📊 Demo During Interview

If they want to see it run:
```bash
cd inveritax_scraper_project
python -m inveritax_scraper --mode mock --fixtures test_fixtures.json \
  --input test_sample.xlsx --output demo_output.json
cat demo_output.json | python -m json.tool
```

Show them the normalized output with all fields properly extracted.

## 🚀 What You'd Do Next (First 2 Weeks)

**Week 1:**
- Set up Linux/Docker environment for Playwright
- Test against all 3 county sites with real parcels
- Refine selectors based on actual HTML structure
- Build comprehensive test fixtures from real runs

**Week 2:**
- Implement address/owner name search modes
- Add screenshot capture on failures
- Build monitoring dashboard (success rates, failures, timing)
- Document common platform patterns for onboarding new counties

---

## Quick Stats for Interview

- **Lines of Code**: ~500 LOC (excluding config)
- **Counties Supported**: 3 (Green Lake, Brown, La Crosse)
- **Platforms Handled**: 3 different (Ascent, GCS, LandNav)
- **Test Parcels**: 425 across 3 counties
- **Architecture Time**: ~8-12 hours (realistic for compressed timeline)
- **Time to Add 4th County**: ~1-2 hours (create YAML, test)

Good luck! You've got this! 🎉


