from pathlib import Path
from inveritax_scraper.input_loader import load_parcels_from_excel

def test_load_parcels():
    xlsx = Path(__file__).parent.parent / "Webscraping Test FIle.xlsx"
    # In CI this file may not exist; this is mainly a local sanity test.
    if not xlsx.exists():
        return
    parcels = load_parcels_from_excel(xlsx)
    assert len(parcels) > 0
