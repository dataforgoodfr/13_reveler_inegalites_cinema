import asyncio
import nodriver as uc
import numpy as np
import os
import pickle as pkl
import time

from bs4 import BeautifulSoup
from multiprocessing import Pool

import festival_constants


d_selectors = {
    'title' : 'css-1kpd5de e3x40ye4',
    'director' : 'css-98s5c8 ekdfppc2',
    'country_and_date' : 'css-1js8va1 e3x40ye11',
    'categories' : 'css-139sg3h e3x40ye12',
    }


async def get_movie_information(page:uc.core.tab.Tab) -> tuple:
    page_content = await page.get_content()
    soup = BeautifulSoup(page_content, 'html.parser')
    title = soup.find('h1', class_=d_selectors['title']).text.strip()
    director = soup.find('span', class_=d_selectors['director']).text.strip()
    country_and_date = soup.find('div', class_=d_selectors['country_and_date']).text.strip()
    categories = soup.find('div', class_=d_selectors['categories']).text.strip()
    runtime = soup.find('time', {'itemprop' : 'duration'}).text.strip()
    image_url = soup.find('meta', {'property' : 'og:image'})['content'].strip()
    try:
        trailer_url = soup.find('meta', {'property' : 'og:video:url'})['content'].strip()
    except TypeError:
        trailer_url = ''
    mubi_id = int(image_url.split('/')[5])
    return title, mubi_id, director, country_and_date, categories, runtime, image_url, trailer_url


async def get_movie_mubi_awards(page:uc.core.tab.Tab) -> tuple[list[str, str, str]]:
    page_content = await page.get_content()
    page_soup = BeautifulSoup(page_content, 'html.parser')
    festival_infos = page_soup.find_all('a', class_='css-pgwez eajdb4a4')
    award_infos = page_soup.find_all('div', class_='css-16kkjs eajdb4a6')

    festival_names = [festival_info.text for festival_info in festival_infos]
    festival_urls = [festival_info['href'] for festival_info in festival_infos]
    award_infos = [award_info.text for award_info in award_infos]
    awards = [[award_info, festival_name, festival_url] for award_info, festival_name, festival_url in zip(award_infos, festival_names, festival_urls, strict=False)]
    return awards


async def get_info_single_movie(movie_url:str, page:uc.core.tab.Tab) -> None:
    if movie_url[:3] == "/en":
        movie_url = "/fr" + movie_url[3:]
    if movie_url[0] == "/":
        movie_url = movie_url[1:]

    page = await page.get(
        f'https://mubi.com/{movie_url}'
    )
    time.sleep(3*np.random.random() + 1)
    title, mubi_id, director, country_and_date, categories, runtime, image_url, trailer_url = await get_movie_information(page)
    
    page = await page.get(
        f'https://mubi.com/{movie_url}/awards/'
    )
    time.sleep(3*np.random.random() + 1)
    awards = await get_movie_mubi_awards(page)
    d_movie = {
        "title" : title,
        "mubi_id" : mubi_id,
        "director" : director,
        "country_and_date" : country_and_date,
        "categories" : categories,
        "runtime" : runtime,
        "image_url" : image_url,
        "trailer_url" : trailer_url,
        "awards" : awards,
        "movie_url" : movie_url,
    }
    with open(os.path.join('movie_data', f'{mubi_id}.pkl'), 'wb') as outfile:
        pkl.dump(d_movie, outfile)
    outfile.close()


async def get_info_list_movies(movie_list:list[str]) -> None:
    browser = await uc.start()
    page = await browser.get(festival_constants.MUBI_BASE_URL)
    os.makedirs("movie_data", exist_ok=True)
    for movie_url in movie_list:
        try:
            await get_info_single_movie(movie_url, page)
            with open('processed_downloads.pkl', 'rb') as infile:
                processed_downloads = pkl.load(infile)
            infile.close()
            processed_downloads.append(movie_url)
            with open('processed_downloads.pkl', 'wb') as outfile:
                pkl.dump(processed_downloads, outfile)
            outfile.close()

        except AttributeError:
            with open('failed_downloads.pkl', 'rb') as infile:
                failed_downloads = pkl.load(infile)
            infile.close()
            failed_downloads.append(movie_url)
            with open('failed_downloads.pkl', 'wb') as outfile:
                pkl.dump(failed_downloads, outfile)
            outfile.close()
    
    
async def test_page_content(page:uc.core.tab.Tab) -> None:
    test_content = await page.find_element_by_text('Oops, we don’t have this information yet.')
    if test_content.text == 'Oops, we don’t have this information yet. Please check back later.' :
        raise ValueError('Page not found.')

    
async def get_festival_year(page:uc.core.tab.Tab, festival:str, year:int) -> None:
    await page.get(f'{festival_constants.MUBI_BASE_URL}/{festival}?year={year}')
    await test_page_content(page)
    time.sleep(3*np.random.random())

    
async def get_movie_urls_from_page(page:uc.core.tab.Tab) -> list[str]:
    content = await page.get_content()
    soup = BeautifulSoup(content, 'html.parser')
    all_movies_page = soup.find_all('a', class_='css-122y91a expqqu72')
    movie_urls = [movie['href'] for movie in all_movies_page]
    return movie_urls
    
    
async def get_all_movies_for_year_festival(page:uc.core.tab.Tab, festival:str, year:int) -> None:
    os.makedirs('festival_data', exist_ok=True)
    os.makedirs(os.path.join('festival_data', festival), exist_ok=True)
    next_button = await page.select('.e1sjp3u22')
    all_movie_urls = []
    if next_button :
        while "#9B9B9B" not in str(next_button) :
            list_movie_urls = await get_movie_urls_from_page(page)
            all_movie_urls += list_movie_urls
            await next_button.click()
            time.sleep(3*np.random.random())
            next_button = await page.select('.e1sjp3u22')
        
    list_movie_urls = await get_movie_urls_from_page(page)
    all_movie_urls += list_movie_urls
    with open(f'festival_data/{festival}/{festival}_{year}.pkl', 'wb') as outfile:
        pkl.dump(all_movie_urls, outfile)
    outfile.close()


def parse_festival_results() -> set:
    festival_list = os.listdir('festival_data')
    all_movie_urls = []
    for festival in festival_list:
        all_years_festival = os.listdir(os.path.join('festival_data', festival))
        for year_festival in all_years_festival:
            with open(os.path.join('festival_data', festival, year_festival), 'rb') as infile:
                yearly_festival_data = pkl.load(infile)
            infile.close()
            all_movie_urls += yearly_festival_data
            
    return set(all_movie_urls)

    
async def extract_all_movie_urls_festival(festival:str, year_start:int, year_stop:int) -> None:
    browser = await uc.start()
    page = await browser.get(f'{festival_constants.MUBI_BASE_URL}')
    if f'{festival}' in os.listdir('festival_data'):
        downloaded_years = os.listdir(f'festival_data/{festival}')
    else :
        downloaded_years = []
    for year in range(year_start, year_stop + 1):
        if f'{festival}_{year}.pkl' in downloaded_years:
            continue
        print(f'\r{festival=}, {year}/{year_stop}', end = '')
        
        try: 
            await get_festival_year(page, festival, year)
        except ValueError:
            continue
        
        await get_all_movies_for_year_festival(page, festival, year)
    browser.stop()
    

async def extract_all_movie_urls_all_festivals(year_start:int, year_stop:int) -> None:
    all_festivals = festival_constants.festival_name_urls
    for _, festival_url in all_festivals.items() :
        if festival_url :
            await extract_all_movie_urls_festival(festival_url, year_start, year_stop)
        

def open_all_festival_movies() -> list[str]:
    all_festival_movies = []
    for folder in os.listdir('festival_data'):
        for item in os.listdir(os.path.join('festival_data', folder)):
            with open(os.path.join('festival_data', folder, item), 'rb') as infile:
                festival_movies = pkl.load(infile)
            infile.close()
            all_festival_movies += festival_movies
    return sorted(list(set(all_festival_movies)))


def split_download_urls(urls:list[str], n_workers:int = 4) -> list[list[str]]:
    split_urls = []
    for n in range(n_workers):
        split_urls.append(urls[n*len(urls)//n_workers:(n+1)*len(urls)//n_workers])
    return split_urls


def run_scraping(list_urls:list[str]) -> None:
    asyncio.run(get_info_list_movies(list_urls))


def run_parallel_scraping(from_scratch:bool = False, n_workers:int = 4, n_downloads:int = 1e6) -> None:
    if 'failed_downloads.pkl' not in os.listdir():
        pkl.dump([], open('failed_downloads.pkl', 'wb'))
        pkl.dump([], open('processed_downloads.pkl', 'wb'))

    all_urls = open_all_festival_movies()
    if not from_scratch:
        processed_downloads = pkl.load(open('processed_downloads.pkl', 'rb'))
        failed_downloads = pkl.load(open('failed_downloads.pkl', 'rb'))
        all_urls = sorted(list(set(all_urls) - set(processed_downloads + failed_downloads)))
        
    split_urls = split_download_urls(all_urls[:int(n_downloads)], n_workers)
    print(f'Parsing {len(all_urls)} urls...')

    with Pool(n_workers) as p:
        p.map(run_scraping, split_urls)

            
# async def run_parallel_scraping(n_workers:int = 4) -> None:
#     all_urls = open_all_festival_movies()
#     split_urls = split_download_urls(all_urls[:20], n_workers)

#     tasks = [get_info_list_movies(split_urls[i]) for i in range(n_workers)]
#     await asyncio.gather(*tasks)

