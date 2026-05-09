import json
import random
from os import getenv
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from urllib.request import urlopen

from playwright.async_api import async_playwright

# Define this variable in docker-compose environment (see database/README)
CHROMIUM_WS_ENDPOINT = getenv("PLAYWRIGHT_WS_ENDPOINT")

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)
DEFAULT_VIEWPORT = {"width": 1280, "height": 800}
DEFAULT_LOCALE = "fr-FR"
BLOCKED_STATUS_CODES = {403, 429}
BLOCKED_PAGE_MARKERS = [
    "captcha",
    "access denied",
    "forbidden",
    "too many requests",
    "verify you are human",
    "bot detection",
]


class WebsiteBlockedError(RuntimeError):
    """Raised when a target website appears to be blocking automated access."""


def _human_like_delay_ms() -> float:
    return random.uniform(1500, 3000)


def _human_like_scroll_y() -> float:
    return random.uniform(500, 3000)


def _merge_query_params(url: str, extra_params: dict[str, str]) -> str:
    parsed = urlparse(url)
    query_params = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query_params.update(extra_params)
    return urlunparse(parsed._replace(query=urlencode(query_params)))


class AsyncBrowserSession:
    """
    Context manager for interacting with a Playwright-controlled browser
    in a realistic, human-like way.
    """

    def __init__(
        self,
        ws_endpoint=CHROMIUM_WS_ENDPOINT,
        user_agent=None,
        stealth=True,
        solve=True,
    ):
        self.ws_endpoint = ws_endpoint
        self.user_agent = user_agent or DEFAULT_USER_AGENT
        self.stealth = stealth
        self.solve = solve
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def _browserless_query_params(self) -> dict[str, str]:
        params = {}
        if self.solve:
            params["solve"] = "true"
        return params

    def _resolve_cdp_endpoint(self) -> str:
        if not self.ws_endpoint:
            raise RuntimeError("PLAYWRIGHT_WS_ENDPOINT is not set")

        parsed = urlparse(self.ws_endpoint)
        browserless_params = self._browserless_query_params()

        # Accept direct websocket endpoints as-is. This supports Browserless-style
        # root websocket URLs as well as explicit `/devtools/browser/...` endpoints.
        if parsed.scheme in {"ws", "wss"}:
            return _merge_query_params(self.ws_endpoint, browserless_params)

        if parsed.scheme not in {"http", "https", "ws", "wss"}:
            raise RuntimeError(
                f"Unsupported PLAYWRIGHT_WS_ENDPOINT scheme: {parsed.scheme or 'missing'}"
            )

        http_scheme = "https" if parsed.scheme in {"https", "wss"} else "http"
        version_url = urlunparse(
            (http_scheme, parsed.netloc, "/json/version", "", parsed.query, "")
        )

        try:
            with urlopen(version_url, timeout=5) as response:
                payload = json.load(response)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to resolve CDP websocket from {version_url}: {exc}"
            ) from exc

        ws_url = payload.get("webSocketDebuggerUrl")
        if not ws_url:
            raise RuntimeError(
                f"No webSocketDebuggerUrl found in {version_url} response"
            )
        return _merge_query_params(ws_url, browserless_params)

    async def __aenter__(self):
        """Setup browser session with anti-bot scripts and open a new page."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.connect_over_cdp(
            self._resolve_cdp_endpoint()
        )
        self.context = await self.browser.new_context(
            user_agent=self.user_agent,
            viewport=DEFAULT_VIEWPORT,
            locale=DEFAULT_LOCALE,
        )
        if self.stealth:
            await self.context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
                Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr'] });
            """)
        self.page = await self.context.new_page()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Gracefully close all browser resources."""
        await self.page.close()
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()

    async def fetch_html(self, url: str) -> str:
        """
        Navigate to a URL, simulate human-like scrolling and waiting,
        and return the resulting HTML content.
        """
        response = await self.page.goto(url)
        if response is not None and response.status in BLOCKED_STATUS_CODES:
            raise WebsiteBlockedError(
                f"Website blocked the request for {url} with HTTP status {response.status}."
            )

        await self.page.wait_for_timeout(_human_like_delay_ms())
        await self.page.mouse.wheel(0, _human_like_scroll_y())
        await self.page.wait_for_timeout(_human_like_delay_ms())
        html = await self.page.content()
        lowered_html = html.lower()

        for marker in BLOCKED_PAGE_MARKERS:
            if marker in lowered_html:
                raise WebsiteBlockedError(
                    f"Website blocking page detected for {url}: found marker '{marker}'."
                )

        return html
