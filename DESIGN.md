# Design Notes (Interview Talking Points)

## Core principle
Separate the reusable engine from per-county variability:
- Engine/orchestrator: concurrency, retries, execution, output
- County config: URL, search workflow, selectors, field mappings

## Adding a new county
1) Add a `county_configs/<county>.yaml`
2) Tune selectors by inspecting the site
3) No Python changes required unless the platform is fundamentally new

## Resilience to change
- Prefer stable selectors (form input names, aria-labels, data-testid) over brittle CSS positions
- Keep extraction rules in YAML so maintenance is config-only
- Capture screenshots/HTML on failures for fast debugging (next step)

## Scaling to 72 counties
- Framework: 2-3 weeks
- Per county onboarding: 0.5-2 days depending on site complexity
- Maintenance: mostly config updates + occasional engine improvements
