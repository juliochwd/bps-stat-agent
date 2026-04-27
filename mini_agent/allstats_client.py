"""
BPS AllStats Search client using Playwright.

Search engine: https://searchengine.web.bps.go.id
URL format: /search?mfd={domain}&q={keyword}&content=all&page=1&title=0&from=all&to=all&sort=terbaru

Access: Requires Playwright + Chromium (bypasses Cloudflare)

Usage:
    client = AllStatsClient(headless=True)
    results = await client.search("data inflasi", domain="5300")
    await client.close()
"""

import asyncio
import sys
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote

try:
    from playwright.async_api import async_playwright
except ImportError:
    raise ImportError("playwright not installed. Run: pip install playwright && playwright install chromium")


@dataclass
class AllStatsResult:
    """Single search result."""

    title: str
    url: str
    snippet: str
    content_type: str
    domain_name: str = ""
    domain_code: str = ""
    year: str = ""
    source: str = "allstats"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AllStatsSearchResponse:
    """Paginated search response."""

    keyword: str
    content_type: str
    page: int
    total_results: int
    per_page: int
    results: list[AllStatsResult]
    has_next: bool
    has_prev: bool
    search_url: str
    _meta: dict[str, Any] = field(default_factory=dict)


class AllStatsClient:
    """Playwright-based client for BPS AllStats Search."""

    BASE_URL = "https://searchengine.web.bps.go.id"
    DEFAULT_TIMEOUT = 30
    DEFAULT_HEADLESS = True
    DEFAULT_SEARCH_DELAY = 10  # Seconds between searches (avoid Cloudflare rate-limit)

    CONTENT_TYPES = {
        "all": "all",
        "publication": "publication",
        "table": "table",
        "pressrelease": "pressrelease",
        "infographic": "infographic",
        "microdata": "microdata",
        "news": "news",
        "glosarium": "glosarium",
        "kbli2020": "kbli2020",
        "kbli2017": "kbli2017",
        "kbli2015": "kbli2015",
        "kbli2009": "kbli2009",
        "kbki2015": "kbki2015",
    }

    SORT_OPTIONS = {
        "relevansi": "relevansi",
        "terbaru": "terbaru",
        "terlama": "terlama",
    }

    def __init__(self, headless: bool = True, timeout: int = 30, search_delay: float = None):
        self.headless = headless
        self.timeout = timeout
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self._last_search_time = 0
        self._search_delay = search_delay if search_delay is not None else self.DEFAULT_SEARCH_DELAY

    def _build_url(
        self,
        keyword: str,
        domain: str = "0000",
        content: str = "all",
        page: int = 1,
        sort: str = "terbaru",
    ) -> str:
        """Build search URL from parameters."""
        q = quote(keyword, safe="")
        return (
            f"{self.BASE_URL}/search"
            f"?mfd={domain}"
            f"&q={q}"
            f"&content={content}"
            f"&page={page}"
            f"&title=0"
            f"&from=all"
            f"&to=all"
            f"&sort={sort}"
        )

    async def _ensure_browser(self):
        """Ensure browser is initialized with anti-detection measures."""
        if self._browser is None:
            self._playwright = await async_playwright().start()
            self._browser = await self._launch_browser()
            self._context = await self._browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                locale="en-US",
                timezone_id="America/New_York",
                permissions=["geolocation"],
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Cache-Control": "max-age=0",
                },
            )

            # Apply stealth anti-detection scripts
            await self._context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                window.chrome = { runtime: {} };
            """)

            self._page = await self._context.new_page()
            self._page.set_default_timeout(self.timeout * 1000)

    async def _launch_browser(self):
        """Launch Chromium, installing the Playwright browser if it is missing."""
        try:
            return await self._playwright.chromium.launch(
                headless=self.headless,
                args=self._browser_args(),
            )
        except Exception as exc:
            if "Executable doesn't exist" not in str(exc):
                raise
            await self._install_chromium()
            return await self._playwright.chromium.launch(
                headless=self.headless,
                args=self._browser_args(),
            )

    @staticmethod
    def _browser_args() -> list[str]:
        return [
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-infobars",
            "--disable-notifications",
            "--window-position=0,0",
            "--window-size=1920,1080",
        ]

    async def _install_chromium(self) -> None:
        """Install Chromium for one-command package installs."""
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            "-m",
            "playwright",
            "install",
            "chromium",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
        if process.returncode != 0:
            output = (stdout + stderr).decode("utf-8", errors="replace")
            raise RuntimeError(f"Failed to install Playwright Chromium: {output}")

    async def search(
        self,
        keyword: str,
        domain: str = "0000",
        content: str = "all",
        page: int = 1,
        sort: str = "terbaru",
    ) -> AllStatsSearchResponse:
        """Search BPS AllStats with keyword and filters.

        Args:
            keyword: Search keyword (e.g., "data inflasi")
            domain: BPS domain code (e.g., "5300" for NTT, "0000" for national)
            content: Content type filter
            page: Page number
            sort: Sort order (terbaru/terlama/relevansi)

        Returns:
            AllStatsSearchResponse with results
        """
        # Rate limiting: wait if last search was too recent
        import time

        now = time.time()
        time_since_last = now - self._last_search_time
        if time_since_last < self._search_delay:
            wait_time = self._search_delay - time_since_last
            print(f"[AllStatsClient] Rate-limiting: waiting {wait_time:.1f}s to avoid Cloudflare block...")
            await asyncio.sleep(wait_time)
        self._last_search_time = time.time()

        await self._ensure_browser()
        url = self._build_url(keyword, domain, content, page, sort)
        print(f"[AllStatsClient] Navigating to: {url}")

        # Try with current context, retry with fresh context if blocked
        max_retries = 2
        for attempt in range(max_retries):
            try:
                await self._page.goto(url, wait_until="domcontentloaded", timeout=self.timeout * 1000)
            except Exception as e:
                print(f"[AllStatsClient] Page load error: {e}")
                try:
                    await self._page.goto(url, wait_until="load", timeout=self.timeout * 1000)
                except Exception:
                    pass

            # Wait for Cloudflare challenge to resolve
            await asyncio.sleep(5)

            # Check if blocked by Cloudflare
            page_content = await self._page.content()
            if (
                "Cloudflare" in page_content
                or "Checking your browser" in page_content
                or "Just a moment" in page_content
            ):
                print(f"[AllStatsClient] Blocked by Cloudflare on attempt {attempt + 1}, creating fresh context...")
                # Close and recreate browser context
                if self._context:
                    await self._context.close()
                if self._browser:
                    await self._browser.close()
                self._browser = None
                self._context = None
                self._page = None
                await self._ensure_browser()
                # Wait a bit before retry
                await asyncio.sleep(10)
                continue
            break  # Success - not blocked

        # Parse results - _parse_results returns list of AllStatsResult
        results = await self._parse_results()

        # Extract total results
        total_results = 0
        try:
            result_count_elem = await self._page.query_selector(".result-count, .total-results, [class*='count']")
            if result_count_elem:
                count_text = await result_count_elem.inner_text()
                print(f"[AllStatsClient] Result count text: {count_text}")
                import re

                numbers = re.findall(r"\d+", count_text.replace(".", "").replace(",", ""))
                if numbers:
                    total_results = int(numbers[0])
        except Exception as e:
            print(f"[AllStatsClient] Could not get result count: {e}")

        # Parse pagination
        has_next = False
        has_prev = False
        try:
            # Check for next/prev pagination links
            next_btn = await self._page.query_selector(
                'a[rel="next"], .pagination .next:not(.disabled), li.next:not(.disabled) a'
            )
            prev_btn = await self._page.query_selector(
                'a[rel="prev"], .pagination .prev:not(.disabled), li.prev:not(.disabled) a'
            )
            has_next = next_btn is not None
            has_prev = prev_btn is not None
        except Exception:
            pass

        response = AllStatsSearchResponse(
            keyword=keyword,
            content_type=content,
            page=page,
            total_results=total_results,
            per_page=len(results),
            results=results,
            has_next=has_next,
            has_prev=has_prev,
            search_url=url,
        )

        print(f"[AllStatsClient] Page title: {await self._page.title()}")
        print(f"[AllStatsClient] Found {len(results)} results")
        return response

    async def _parse_results(self) -> list[AllStatsResult]:
        """Parse search results from page HTML using DOM."""
        results = []

        try:
            # Use page.evaluate to parse with DOM and return proper objects
            parsed = await self._page.evaluate("""
                () => {
                    const results = [];
                    
                    // The correct selector for BPS search results
                    const items = document.querySelectorAll('.card-result');

                    items.forEach((item) => {
                        const linkEl = item.querySelector('a');
                        const titleEl = linkEl || item.querySelector('h5, h4, h3, .title');
                        const snippetEl = item.querySelector('.text-muted, .desc, p');
                        const typeEl = item.querySelector('.badge, .category, [class*="type"]');
                        const domainEl = item.querySelector('[class*="domain"]');
                        const yearEl = item.querySelector('[class*="year"], .year');

                        // Get title - could be in link text or heading
                        let title = titleEl?.innerText?.trim() || '';
                        const url = linkEl?.href || '';

                        // If title is URL, get heading instead
                        if (title.includes('bps.go.id') || !title) {
                            const heading = item.querySelector('h5, h4, h3');
                            title = heading?.innerText?.trim() || title;
                        }

                        if (title) {
                            results.push({
                                title: title,
                                url: url,
                                snippet: snippetEl?.innerText?.trim() || '',
                                content_type: typeEl?.innerText?.trim() || '',
                                domain_name: domainEl?.innerText?.trim() || '',
                                domain_code: '',
                                year: yearEl?.innerText?.trim() || '',
                            });
                        }
                    });

                    // Fallback: if no .card-result, try other selectors
                    if (results.length === 0) {
                        const fallbackSelectors = ['.result-item', '.search-result', 'article', '.list-item'];
                        for (const sel of fallbackSelectors) {
                            const fallbackItems = document.querySelectorAll(sel);
                            if (fallbackItems.length > 0) {
                                fallbackItems.forEach(item => {
                                    const link = item.querySelector('a[href*="bps"]');
                                    if (link) {
                                        const heading = item.querySelector('h5, h4, h3');
                                        results.push({
                                            title: heading?.innerText?.trim() || link.innerText,
                                            url: link.href,
                                            snippet: '',
                                            content_type: '',
                                            domain_name: '',
                                            domain_code: '',
                                            year: '',
                                        });
                                    }
                                });
                                break;
                            }
                        }
                    }

                    return results;
                }
            """)

            # Convert dicts to AllStatsResult objects
            for item in parsed:
                results.append(
                    AllStatsResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("snippet", ""),
                        content_type=item.get("content_type", ""),
                        domain_name=item.get("domain_name", ""),
                        domain_code=item.get("domain_code", ""),
                        year=item.get("year", ""),
                    )
                )

            print(f"[AllStatsClient] Parsed {len(results)} results from DOM")
            return results

        except Exception as e:
            print(f"[AllStatsClient] DOM parsing error: {e}")
            import traceback

            traceback.print_exc()
            return results

    async def get_data_page(self, result_url: str) -> dict[str, Any]:
        """Navigate to a search result page and extract data.

        Flow:
        1. Click/open result URL
        2. Infographic popup appears
        3. Close popup
        4. Extract full data from page

        Args:
            result_url: URL of the search result to open

        Returns:
            dict with page data content
        """
        await self._ensure_browser()
        print(f"[AllStatsClient] Opening data page: {result_url}")

        try:
            await self._page.goto(result_url, wait_until="domcontentloaded", timeout=self.timeout * 1000)
            await asyncio.sleep(2)

            # Try to close popup
            await self._close_popup()

            # Wait for content to load
            await asyncio.sleep(2)

            # Extract page content
            content = await self._page.content()
            title = await self._page.title()

            # Extract text content
            text_content = await self._page.evaluate("""
                () => document.body.innerText
            """)

            # Try to find data tables
            tables = await self._page.query_selector_all("table")
            table_data = []
            for table in tables:
                rows = await table.query_selector_all("tr")
                table_rows = []
                for row in rows:
                    cells = await row.query_selector_all("td, th")
                    row_data = [await cell.inner_text() for cell in cells]
                    table_rows.append(row_data)
                table_data.append(table_rows)

            return {
                "title": title,
                "url": result_url,
                "html": content,
                "text": text_content,
                "tables": table_data,
            }
        except Exception as e:
            print(f"[AllStatsClient] Error fetching data page: {e}")
            return {"error": str(e)}

    async def _close_popup(self) -> bool:
        """Close infographic popup if present.

        Returns True if popup was found and closed.
        """
        popup_selectors = [
            ".popup-close",
            ".modal-close",
            ".close-btn",
            ".infographic-close",
            "[aria-label='Close']",
            "[class*='popup'] .close",
            "[class*='modal'] .close",
            ".btn-close",
            "button.close",
        ]

        for selector in popup_selectors:
            try:
                popup = await self._page.query_selector(selector)
                if popup:
                    print(f"[AllStatsClient] Found popup with selector: {selector}")
                    await popup.click()
                    await asyncio.sleep(1)
                    print("[AllStatsClient] Popup closed")
                    return True
            except Exception:
                continue

        # Also try Escape key
        try:
            await self._page.keyboard.press("Escape")
            await asyncio.sleep(0.5)
            print("[AllStatsClient] Tried Escape key")
        except Exception:
            pass

        print("[AllStatsClient] No popup found or could not close")
        return False

    async def close(self):
        """Clean up browser resources."""
        if self._page:
            await self._page.close()
            self._page = None
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        return False


async def main():
    """Test the client."""
    client = AllStatsClient(headless=False)  # Set False to see browser

    try:
        # Test search
        print("=" * 60)
        print("TEST: Search for 'data inflasi' in NTT (domain 5300)")
        print("=" * 60)
        response = await client.search("data inflasi", domain="5300", content="all")

        print(f"\nResults: {len(response.results)}")
        for i, result in enumerate(response.results[:5], 1):
            print(f"\n--- Result {i} ---")
            print(f"Title: {result.title}")
            print(f"URL: {result.url}")
            print(f"Snippet: {result.snippet[:100]}...")
            print(f"Type: {result.content_type}")

        # Try to get data from first result if available
        if response.results:
            first_url = response.results[0].url
            if first_url:
                print("\n" + "=" * 60)
                print(f"TEST: Get data page from: {first_url}")
                print("=" * 60)
                data = await client.get_data_page(first_url)
                if "error" in data:
                    print(f"Error: {data['error']}")
                else:
                    print(f"Page title: {data.get('title', 'N/A')}")
                    print(f"Text content (first 300 chars): {data.get('text', '')[:300]}...")
                    print(f"Tables found: {len(data.get('tables', []))}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
