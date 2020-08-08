import aiohttp
from bs4 import BeautifulSoup as Soup
from loguru import logger

from app.misc import app_dir
from .exceptions import CantImportFromAxenia


def username_by_link(link: str) -> str:
    return link.split('=')[1]


def get_rating(html):
    soup = Soup(html, 'lxml')
    main_soup = soup.find('main', role='main')

    for tbody in main_soup.find('div', class_="carousel-inner").find_all('tbody'):
        for tr in tbody.find_all('tr'):
            tds = tr.find_all('td')
            name = tds[0].text
            try:
                username = username_by_link(tds[0].find('a').get('href'))
            except Exception:
                username = None
            karma = tds[1].text
            yield name, username, karma


def get_html_file():
    html_file = app_dir.parent / 'html' / 'Karmabot for Telegram Axenia.html'
    with html_file.open('r', encoding='UTF-8') as f:
        return f.read()


async def get_html(url):
    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as r:
            if not r.status == 200:
                raise CantImportFromAxenia(chat_id=url.split('=')[1])
            return await r.text()


def get_link_by_chat_id(chat_id: int) -> str:
    return f"http://axeniabot.ru/?chat_id={chat_id}"


async def axenia_raiting(chat_id):
    logger.debug(f"import from {chat_id}")
    return list(
        get_rating(
            await get_html(
                get_link_by_chat_id(chat_id)
            )
        )
    )
