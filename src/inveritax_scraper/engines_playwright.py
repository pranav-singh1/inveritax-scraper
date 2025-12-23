from __future__ import annotations

import asyncio
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

from playwright.sync_api import sync_playwright, Browser, Page

from .engine import ScrapeEngine, ScrapeResult
from .models import ParcelInput


class PlaywrightEngine(ScrapeEngine):
    def __init__(self, *, headless: bool = True, slow_mo_ms: int = 0, timeout_ms: int = 30000):
        self.headless = headless
        self.slow_mo_ms = slow_mo_ms
        self.timeout_ms = timeout_ms
        self._pw = None
        self._browser: Optional[Browser] = None

    async def start(self) -> None:
        def _start():
            self._pw = sync_playwright().start()
            self._browser = self._pw.chromium.launch(headless=self.headless, slow_mo=self.slow_mo_ms)
        await asyncio.to_thread(_start)

    async def stop(self) -> None:
        def _stop():
            if self._browser:
                self._browser.close()
            if self._pw:
                self._pw.stop()
        await asyncio.to_thread(_stop)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.75, min=1, max=8))
    async def fetch(self, *, base_url: str, cfg: Dict[str, Any], parcel: ParcelInput) -> ScrapeResult:
        def _fetch_sync():
            if not self._browser:
                return ScrapeResult(False, error="PlaywrightEngine not started")

            # Create a new context for each request to avoid state issues
            context = self._browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page: Page = context.new_page()
            try:
                import time
                page.set_default_timeout(self.timeout_ms)
                page.goto(base_url, wait_until="domcontentloaded")
                time.sleep(2)

                sel = cfg.get("selectors", {})
                
                # Handle popup/modal dismissal
                popup_dismiss = sel.get("popup_dismiss_selector")
                if popup_dismiss:
                    try:
                        page.click(popup_dismiss, timeout=3000)
                        time.sleep(0.5)
                    except Exception:
                        pass
                
                # Try common popup and guest login patterns
                common_selectors = [
                    'button:has-text("I Accept")',
                    'button:has-text("I understand")',
                    'button:has-text("Accept")',
                    'button:has-text("OK")',
                    'button:has-text("Guest")',
                    'a:has-text("Guest")',
                    'button:has-text("Continue as Guest")',
                    'a:has-text("Previous Page")',
                    '#btnAccept',
                    '#btnOk'
                ]
                clicked_popup = False
                for selector in common_selectors:
                    try:
                        elem = page.query_selector(selector)
                        if elem and elem.is_visible():
                            page.click(selector, timeout=2000)
                            time.sleep(2)  # Give page time to process click
                            clicked_popup = True
                            break
                    except Exception:
                        pass
                
                # If we clicked a popup, wait extra time for page to settle
                if clicked_popup:
                    time.sleep(3)
                
                # Handle guest accept button (La Crosse specific)
                guest_accept = sel.get("guest_accept_selector")
                if guest_accept:
                    try:
                        elem = page.query_selector(guest_accept)
                        if elem and elem.is_visible():
                            page.click(guest_accept, timeout=3000)
                            time.sleep(2)
                    except Exception:
                        pass
                
                # For La Crosse, navigate to search page after accepting
                if 'landnav' in base_url.lower() and '/Home' in base_url:
                    try:
                        page.goto(base_url.replace('/Home', '/Search/RealEstate/Search'))
                        time.sleep(3)
                    except:
                        pass

                tab_selector = sel.get("tab_selector")
                if tab_selector:
                    try:
                        page.click(tab_selector, timeout=3000)
                        time.sleep(0.5)
                    except Exception:
                        pass

                query = parcel.parcel_number
                search_input = sel.get("search_input_selector")
                if search_input:
                    # For Angular apps, wait longer for the page to be ready
                    time.sleep(4)
                    try:
                        # For selectors like "input[type='text']:visible:nth(1)", use special handling
                        if ':visible:nth(' in search_input:
                            # Get all visible inputs and pick the nth one
                            n = int(search_input.split(':nth(')[1].split(')')[0])
                            all_inputs = page.query_selector_all('input[type="text"]')
                            visible_inputs = [inp for inp in all_inputs if inp.is_visible()]
                            if len(visible_inputs) > n:
                                visible_inputs[n].fill(query)
                        else:
                            page.wait_for_selector(search_input, timeout=15000, state="visible")
                            page.locator(search_input).fill(query, force=True, timeout=15000)
                    except Exception as e:
                        # Try without force if force fails
                        try:
                            page.fill(search_input, query, timeout=15000)
                        except:
                            pass

                search_button = sel.get("search_button_selector")
                if search_button:
                    time.sleep(2)
                    # Wait for button to be visible and clickable
                    page.wait_for_selector(search_button, timeout=20000, state="visible")
                    page.wait_for_selector(search_button, timeout=5000, state="attached")
                    page.click(search_button, timeout=15000)
                    time.sleep(6)  # Give Angular time to load results

                wait_for = sel.get("wait_for_selector")
                if wait_for:
                    try:
                        page.wait_for_selector(wait_for, timeout=15000, state="visible")
                    except:
                        # Results might already be there, just not matching our selector
                        time.sleep(2)

                result_row = sel.get("result_row_selector")
                details_link = sel.get("details_link_selector")
                if result_row and details_link:
                    rows = page.query_selector_all(result_row)
                    if rows:
                        link = rows[0].query_selector(details_link)
                        if link:
                            link.click()
                            page.wait_for_load_state("domcontentloaded")
                            time.sleep(1)
                elif details_link:
                    try:
                        page.click(details_link, timeout=10000)
                        page.wait_for_load_state("domcontentloaded")
                        time.sleep(1)
                    except Exception:
                        pass
                
                detail_tab = sel.get("detail_tab_selector")
                if detail_tab:
                    try:
                        page.click(detail_tab, timeout=5000)
                        time.sleep(1)
                    except Exception:
                        pass
                
                taxes_link = sel.get("taxes_link_selector")
                if taxes_link:
                    try:
                        page.click(taxes_link, timeout=5000)
                        time.sleep(2)
                    except Exception:
                        pass

                extraction = sel.get("extract", {})
                data: Dict[str, Any] = {}
                for key, rule in extraction.items():
                    if isinstance(rule, str):
                        el = page.query_selector(rule)
                        data[key] = el.inner_text() if el else None
                    elif isinstance(rule, dict):
                        selector = rule.get("selector")
                        attr = rule.get("attr")
                        if selector:
                            el = page.query_selector(selector)
                            if not el:
                                data[key] = None
                            else:
                                if attr:
                                    data[key] = el.get_attribute(attr)
                                else:
                                    data[key] = el.inner_text()
                    else:
                        data[key] = None

                result = ScrapeResult(True, data=data, source_url=page.url)
                page.close()
                context.close()
                return result
            except Exception as e:
                result = ScrapeResult(False, error=str(e), source_url=getattr(page, "url", None))
                try:
                    page.close()
                    context.close()
                except:
                    pass
                return result
        
        return await asyncio.to_thread(_fetch_sync)


class MockEngine(ScrapeEngine):
    def __init__(self, *, fixtures: Dict[str, Dict[str, Any]]):
        self.fixtures = fixtures

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None

    async def fetch(self, *, base_url: str, cfg: Dict[str, Any], parcel: ParcelInput) -> ScrapeResult:
        key = f"{parcel.county.lower()}::{parcel.parcel_number}"
        if key not in self.fixtures:
            return ScrapeResult(False, error=f"No fixture for {key}")
        data = self.fixtures[key]
        return ScrapeResult(True, data=data, source_url=base_url)
