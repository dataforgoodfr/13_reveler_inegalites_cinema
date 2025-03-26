from playwright.async_api import async_playwright
from os import getenv
import random

# Define this variable in docker-compose environment (see database/README)
CHROMIUM_WS_ENDPOINT = getenv("PLAYWRIGHT_WS_ENDPOINT")

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)
DEFAULT_VIEWPORT = {"width": 1280, "height": 800}
DEFAULT_LOCALE = "fr-FR"
HUMAN_LIKE_DELAY = random.uniform(1500, 3000)
HUMAN_LIKE_SCROLL_Y = random.uniform(500, 3000)


class AsyncBrowserSession:
    """
    Context manager for interacting with a Playwright-controlled browser
    in a realistic, human-like way.
    """

    def __init__(self, ws_endpoint=CHROMIUM_WS_ENDPOINT, user_agent=None):
        self.ws_endpoint = ws_endpoint
        self.user_agent = user_agent or DEFAULT_USER_AGENT
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def __aenter__(self):
        """Setup browser session with anti-bot scripts and open a new page."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.connect_over_cdp(self.ws_endpoint)
        self.context = await self.browser.new_context(
            user_agent=self.user_agent,
            viewport=DEFAULT_VIEWPORT,
            locale=DEFAULT_LOCALE,
        )
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
        await self.page.goto(url)
        await self.page.wait_for_timeout(HUMAN_LIKE_DELAY)
        await self.page.mouse.wheel(0, HUMAN_LIKE_SCROLL_Y)
        await self.page.wait_for_timeout(HUMAN_LIKE_DELAY)
        return await self.page.content()
