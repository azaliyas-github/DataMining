import logging
from typing import List, Set
from urllib.parse import ParseResult, urlparse

from graphviz import Digraph

from implementation.common import page_link_repository_name
from implementation.infrastructure import configure_logging
from implementation.page_link import PageLink, PageLinkRepository

log: logging.Logger = logging.getLogger()


def main() -> None:
    configure_logging()

    page_links: List[PageLink] = get_page_links(page_link_repository_name)

    draw_graph(page_links)


def get_page_links(repository_name: str) -> List[PageLink]:
    log.info("Инициализирую хранилище ссылок " + repository_name)
    page_links_repository: PageLinkRepository = PageLinkRepository(repository_name)

    log.info("Предобрабатываю ссылки")
    page_links: List[PageLink] = page_links_repository.get_all()
    for page_link in page_links:
        page_link.from_url = preprocess_url(page_link.from_url)
        page_link.to_url = preprocess_url(page_link.to_url)

    return page_links


def preprocess_url(url: str) -> str:
    # Убираем схему
    parsed_url: ParseResult = urlparse(url)
    scheme: str = parsed_url.scheme + "://"
    url = parsed_url.geturl().replace(scheme, "", 1)

    url = url.replace(":", "")

    return url


def draw_graph(page_links: List[PageLink]) -> None:
    graph: Digraph = Digraph()
    created_nodes: Set[str] = set()  # множество URL, для которых уже созданы узлы графа

    def create_node(url: str) -> None:
        graph.node(url, url)
        created_nodes.add(url)

    log.info(f"Создаю граф из {len(page_links)} ссылок")
    for link in page_links:
        if link.from_url not in created_nodes:
            create_node(link.from_url)
        if link.to_url not in created_nodes:
            create_node(link.to_url)

        graph.edge(link.from_url, link.to_url)

    log.info("Рисую граф ссылок")
    graph.view()


if __name__ == '__main__':
    main()
