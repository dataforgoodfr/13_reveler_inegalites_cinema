from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import os

CHROMIUM_WS_ENDPOINT = os.getenv("PLAYWRIGHT_WS_ENDPOINT")

# Url to scrap MUBI festivals
BASE_URL = "https://mubi.com"
ALL_FESTIVALS_URL = f"{BASE_URL}/fr/awards-and-festivals?type={{festival_or_award}}&page={{page_num}}"

DEFAULT_FESTIVALS_FILTERS = {
  "page_num": "1",
  "festival_or_award": "festival",
}

MUBI_FESTIVALS_CLASSES = {
  "festival": "div.css-te72z8",
  "festival_link": "a.css-13zcxcg",
  "festival_name": "div.css-1o91brm"
}

# Scraping MUBI website method
async def scrap_mubi_film_festivals(filters = DEFAULT_FESTIVALS_FILTERS):
  generated_url = ALL_FESTIVALS_URL.format(**filters)

  async with async_playwright() as p:
    # Simulate a real browser to get the full page content
    browser = await p.chromium.connect_over_cdp(CHROMIUM_WS_ENDPOINT)  # Connect to remote Chromium
    context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    page = await context.new_page()
    
    await page.goto(generated_url) #, wait_until="networkidle")
    await page.wait_for_timeout(2000)
    await page.mouse.wheel(0, 1000)
    await page.wait_for_timeout(2000)

    html = await page.content()
    with open("mubi_film.html", "w") as file:
        file.write(html)

    # Extract from page content the movies data
    soup = BeautifulSoup(html, "html.parser")
    festival_elements = soup.select(MUBI_FESTIVALS_CLASSES["festival"])
    festivals = []
    for festival in festival_elements:
        festival_link = festival.select_one(MUBI_FESTIVALS_CLASSES["festival_link"])
        festival_name = festival.select_one(MUBI_FESTIVALS_CLASSES["festival_name"])

        festival_data = {
            "festival_link": festival.get_text(strip=True) if festival_link else None,
            "festival_name": reward.get_text(strip=True) if festival_name else None,
        }

        festivals.append(festival_data)

    await browser.close()
    return festivals


# Run the scraping method
await scrap_mubi_film_festivals()
