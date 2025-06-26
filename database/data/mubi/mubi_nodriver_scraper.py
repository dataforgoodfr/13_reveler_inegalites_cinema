import nodriver as uc
import numpy as np
import pickle as pkl
import os
import time

from bs4 import BeautifulSoup

import festival_constants


async def get_movie_mubi_id(page:uc.core.tab.Tab) -> int:
    page_content = await page.get_content()
    soup = BeautifulSoup(page_content)
    link = soup.find("meta", property="og:image")['content']
    mubi_id = link.split('/')[5]
    return int(mubi_id)


async def get_movie_mubi_awards(page:uc.core.tab.Tab) -> list[str, str, str]:
    page_content = await page.get_content()
    page_soup = BeautifulSoup(page_content, 'html.parser')
    festival_infos = page_soup.find_all('a', class_='css-pgwez eajdb4a4')
    #festival_urls = page_soup.find_all('a', class_='css-pgwez eajdb4a4')
    award_infos = page_soup.find_all('div', class_='css-16kkjs eajdb4a6')

    # festival_names = [festival_name.text for festival_name in festival_names]
    # festival_urls = [festival_url['href'] for festival_url in festival_urls]
    festival_names = [festival_info.text for festival_info in festival_infos]
    festival_urls = [festival_info['href'] for festival_info in festival_infos]
    award_infos = [award_info.text for award_info in award_infos]
    awards = [[award_info, festival_name, festival_url] for award_info, festival_name, festival_url in zip(award_infos, festival_names, festival_urls, strict=False)]
    return awards


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
        
