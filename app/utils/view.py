from aiogram.utils.text_decorations import html_decoration as hd


def hidden_link(url: str) -> str:
    return hd.link("&#8288;", url)
