import logging
import os
import re as regex
import sys
from collections import deque
from itertools import chain
from urllib.parse import urldefrag, urljoin

import requests
from bs4 import BeautifulSoup

from implementation.infrastructure import configure_logging, format_exception
from implementation.page_link import PageLink, PageLinkRepository

log = logging.getLogger()
pages_availability = {}

max_depth = 3
page_link_repository_name = "page-links"


def main():
    root_page_url = get_root_page_url()
    if root_page_url is None:
        return

    configure_logging()

    collect_web_pages(root_page_url)


def collect_web_pages(root_page_url):
    log.info("Инициализирую хранилище ссылок")
    page_links = PageLinkRepository(page_link_repository_name)
    page_links.delete_all()

    # Очередь, в которой хранятся следующие для загрузки ссылки в виде пар (URL, глубина)
    page_urls_to_download = deque([(root_page_url, 0)])  # очередь содержащая словарь из корневой ссылки и 0
    seen_page_urls = {root_page_url}  # множество просмотренных страниц
    current_depth = 0
    # Пока есть ссылки на страницы, которые можно скачать
    # и пока скачали меньше, чем нужно
    while len(page_urls_to_download) > 0 and current_depth < max_depth:
        page_url, current_depth = page_urls_to_download.popleft()
        log.info("Скачиваю страницу " + page_url)
        unparsed_html_page = download(page_url)
        if unparsed_html_page is None:
            continue
        if issubclass(type(unparsed_html_page), Exception):
            log.warning(f"Не смог скачать страницу {page_url}:" + os.linesep
                        + format_exception(unparsed_html_page))
            continue

        try:
            parsed_html_page = BeautifulSoup(unparsed_html_page, "html.parser")
        except Exception as exception:
            log.warning(
                f"Не смог распознать страницу {page_url} как HTML:" + os.linesep + format_exception(exception))
            continue

        page_content = get_content(parsed_html_page)
        child_urls = list(get_link_urls(page_url, parsed_html_page, page_content))

        log.info("Сохраняю ссылки со страницы " + page_url)
        link_counts = {}
        for to_url in child_urls:
            if not check_availability(to_url):
                continue

            link_counts.setdefault(to_url, 1)
            link_counts[to_url] += 1

        for to_url, count in link_counts.items():
            page_link = PageLink(current_depth, page_url, to_url, count)
            try:
                page_links.create(page_link)
            except Exception as exception:
                log.error(
                    f"Не смог сохранить ссылку с \"{page_url}\" на \"{to_url}\":" + os.linesep
                    + format_exception(exception))

        if current_depth < max_depth:
            # возвращается разница дочерних и просмотренных ссылок
            child_urls = list(filter(
                lambda url: url not in seen_page_urls,
                link_counts.keys()))
            child_urls = [(url, current_depth + 1) for url in child_urls]  # кортеж

            page_urls_to_download.extend(child_urls)
            seen_page_urls = seen_page_urls.union(child_urls)


def get_root_page_url():
    if len(sys.argv) == 2:
        return sys.argv[1]

    return input("URL: ")


def check_status_code(response):
    return 200 <= response.status_code < 300


def check_availability(url):
    is_available = pages_availability.get(url)
    if is_available is not None:
        return is_available

    # noinspection PyBroadException
    try:
        response = requests.get(url, headers={"accept": "text/html"}, allow_redirects=False, stream=True)
        is_available = check_status_code(response)
        response.close()
    except Exception:
        is_available = False

    pages_availability[url] = is_available
    return is_available


def download(url):
    is_available = pages_availability.get(url)
    if is_available is not None and not is_available:
        return None

    try:
        response = requests.get(url, headers={"accept": "text/html"}, allow_redirects=False, stream=True)
        if not check_status_code(response):
            return None

        content_type = response.headers.get("content-type")
        if content_type is None or len(content_type) == 0:
            return ValueError("Получил страницу с пустым Content-Type")
        if "html" not in content_type:
            return ValueError("Получил страницу с неизвестным Content-Type: " + content_type)

        return response.text
    except Exception as error:
        return error


def get_link_urls(current_url, html, content):
    if html.body is None:
        return []

    # Берём ссылки из <a href="...">
    a_tags = html.body.find_all("a")
    urls = (tag.get("href", default="") for tag in a_tags)

    # Берём URL из контента страницы
    links_from_content = (
        url.group(0).split()[0]
        for url in regex.finditer(
            "((https?|ftp)://|(www|ftp)\\.)?[a-z0-9-]+(\\.[a-z0-9-]+)+([/?].*)?",
            content))
    urls = chain(urls, links_from_content)

    # Делаем из относительных URL абсолютные
    urls = (urljoin(current_url, url) for url in urls)

    # Убираем якори из URL
    urls = (urldefrag(url).url for url in urls)

    return urls


def get_content(html):
    return html.get_text(" ")


if __name__ == '__main__':
    main()
