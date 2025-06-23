
from typing import Dict
from bs4 import BeautifulSoup



def get_mubi_id(page) -> int:
    page_content = await page.get_content()
    soup = BeautifulSoup(page_content)
    link = soup.find("meta", property="og:image")['content']
    mubi_id = link.split('/')[5]
    return int(mubi_id)
    

def get_mubi_awards(page) -> Dict:
    page_content = await page.get_content()
    page_soup = BeautifulSoup(page_content, 'html.parser')
    festival_names = page_soup.find_all('a', class_='css-pgwez eajdb4a4')
    festival_urls = page_soup.find_all('a', class_='css-pgwez eajdb4a4')
    award_infos = page_soup.find_all('div', class_='css-16kkjs eajdb4a6')

    festival_names = [festival_name.text for festival_name in festival_names]
    festival_urls = [festival_url['href'] for festival_url in festival_urls]
    award_infos = [award_info.text for award_info in award_infos]
