from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import os

CHROMIUM_WS_ENDPOINT = os.getenv("PLAYWRIGHT_WS_ENDPOINT")

# Url to scrap MUBI festivals
BASE_URL = "https://mubi.com"
FESTIVAL_URL = f"{BASE_URL}/fr/awards-and-festivals/{{festival}}?page={{page_num}}&year={{year}}"

AWARDS_MUBI_LIST = ["oscars", "cesars", "baftas", "golden-globes"]
FESTIVALS_MUBI_LIST = ["cannes", "venice", "berlinale"]

DEFAULT_FESTIVAL_FILTERS = {
  "festival": "cesars",
  "page_num": "1",
  "year": "2024",
}

MUBI_FILMS_CLASSES = {
  "movie": "li.css-1ncbtb3", # li - css-1ncbtb3 ejkdwq71
  "nominations": "div.css-gyp8mm", # div - css-gyp8mm eiz03ik4 OR div - css-ko5a18 eiz03ik1
  "title": "h3.css-1hr6q83", # h3 - css-1hr6q83 e1fxv8uz1
  "director": "span.css-1vg6q84", # span - css-1vg6q84 e1slvksg0
  "country": "span.css-ahepiu", # span - css-ahepiu epl1xvv1
  "link": "a.css-122y91a" # css-122y91a e8qvidc2
}

# Scraping MUBI website method
async def scrap_mubi_festivals(filters = DEFAULT_FESTIVAL_FILTERS):
  generated_url = FESTIVAL_URL.format(**filters)

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

    # Extract from page content the movies data
    soup = BeautifulSoup(html, "html.parser")
    movie_elements = soup.select(MUBI_FILMS_CLASSES["movie"])
    movies = []
    for movie in movie_elements:
        title = movie.select_one(MUBI_FILMS_CLASSES["title"])
        director = movie.select_one(MUBI_FILMS_CLASSES["director"])
        country = movie.select_one(MUBI_FILMS_CLASSES["country"])
        nominations = movie.select_one(MUBI_FILMS_CLASSES["nominations"])
        link = movie.select_one(MUBI_FILMS_CLASSES["link"])

        movie_data = {
            "title": title.get_text(strip=True) if title else None,
            "director": director.get_text(strip=True) if director else None,
            "country": country.get_text(strip=True) if country else None,
            "nominations": nominations.get_text(strip=True) if nominations else None,
            "link": link["href"] if link else None
        }

        movies.append(movie_data)

    await browser.close()
    return movies


# Run the scraping method
await scrap_mubi_festivals()