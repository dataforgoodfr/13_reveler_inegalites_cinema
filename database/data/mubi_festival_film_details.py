from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import os

CHROMIUM_WS_ENDPOINT = os.getenv("PLAYWRIGHT_WS_ENDPOINT")

# Url to scrap MUBI festivals
BASE_URL = "https://mubi.com"
FILM_URL = f"{BASE_URL}{{film_link}}/awards"

DEFAULT_FILM_FILTERS = {
  "film_link": "/fr/fr/films/the-substance"
}

MUBI_FILM_CLASSES = {
  "award": "div.css-epmkt5",
  "festival": "a.css-pgwez",
  "reward": "div.css-16kkjs",
}

# Scraping MUBI website method
async def scrap_mubi_film_awards(filters = DEFAULT_FILM_FILTERS):
  generated_url = FILM_URL.format(**filters)

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
    award_elements = soup.select(MUBI_FILM_CLASSES["award"])
    awards = []
    for award in award_elements:
        festival = award.select_one(MUBI_FILM_CLASSES["festival"])
        reward = award.select_one(MUBI_FILM_CLASSES["reward"])

        award_data = {
            "festival": festival.get_text(strip=True) if festival else None,
            "reward": reward.get_text(strip=True) if reward else None,
        }

        awards.append(award_data)

    await browser.close()
    return awards


# Run the scraping method
await scrap_mubi_film_awards()
