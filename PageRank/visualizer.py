import logging
from typing import Dict, List, Set, Tuple
from urllib.parse import ParseResult, urlparse

from py2cytoscape.data.cynetwork import CyNetwork
from py2cytoscape.data.cyrest_client import CyRestClient

from implementation.common import page_link_repository_name
from implementation.infrastructure import configure_logging
from implementation.page_link import PageLink, PageLinkRepository

log: logging.Logger = logging.getLogger()

layout_name = "circular"


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

    return url


def draw_graph(page_links: List[PageLink]) -> None:
    log.info(f"Создаю граф из {len(page_links)} ссылок")
    graph_nodes: Set[str] = set()
    graph_edges: List[Tuple[str, str]] = []
    for link in page_links:
        if link.from_url not in graph_nodes:
            graph_nodes.add(link.from_url)
        if link.to_url not in graph_nodes:
            graph_nodes.add(link.to_url)

        graph_edges.append((link.from_url, link.to_url))

    log.info("Рисую граф ссылок с расположением " + layout_name)
    cytospace_client: CyRestClient = CyRestClient()
    graph: CyNetwork = cytospace_client.network.create()

    node_suids: Dict[str, int] = graph.add_nodes(list(graph_nodes))
    graph.add_edges(list(
        {"source": node_suids[edge[0]], "target": node_suids[edge[1]]}
        for edge in graph_edges))
    cytospace_client.layout.apply(layout_name, graph)

    image_height: int = max(len(graph_nodes) * 60, 600)
    graph_image: bytes = graph.get_png(image_height)
    with open(f"links-{layout_name}.png", "wb+") as png_file:
        png_file.write(graph_image)


if __name__ == '__main__':
    main()
