import logging
from argparse import Namespace
from typing import Dict, List, Set, Tuple
from urllib.parse import ParseResult, urlparse

from pandas import DataFrame
from py2cytoscape.data.cynetwork import CyNetwork
from py2cytoscape.data.cyrest_client import CyRestClient

from implementation.common import page_link_repository_name
from implementation.configuration import SafeArgumentParser
from implementation.infrastructure import get_logger
from implementation.page_link import PageLink, PageLinkRepository
from page_ranker import build_transition_matrix

log: logging.Logger = get_logger()

max_url_length: int = 60


def main() -> None:
    configuration: Namespace = get_configuration()

    page_links: List[PageLink] = get_page_links(page_link_repository_name)
    page_links = merge_duplicate_page_links(page_links)

    if configuration.save_matrix:
        index, matrix = build_transition_matrix(page_links)
        save_transition_matrix(index, matrix)
    if configuration.draw_graph:
        draw_graph(page_links, configuration.layout_name)


def get_configuration(unparsed_args: List[str] = None) -> Namespace:
    argument_parser: SafeArgumentParser = SafeArgumentParser()
    argument_parser.add_argument("layout_name", metavar = "layout-name")
    argument_parser.add_argument("--no-save-matrix", dest = "save_matrix", action = "store_false")
    argument_parser.add_argument("--no-draw-graph", dest = "draw_graph", action = "store_false")
    args: Namespace = argument_parser.parse_args(unparsed_args)

    if args.layout_name is None:
        args.layout_name = input("Layout: ")

    return args


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

    url = url[:max_url_length]

    return url


def merge_duplicate_page_links(page_links: List[PageLink]) -> List[PageLink]:
    merged_page_links: Dict[Tuple[str, str], int] = dict()

    for link in page_links:
        link_key: Tuple[str, str] = (link.from_url, link.to_url)
        merged_page_links[link_key] = merged_page_links.setdefault(link_key, 0) + link.count

    return [
        PageLink(0, from_url, to_url, count)
        for (from_url, to_url), count in merged_page_links.items()]


def draw_graph(page_links: List[PageLink], layout_name: str) -> None:
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

    # 24000 пикселей — максимальная высота изображения; это ограничение накладывает Cytospace
    image_height: int = min(max(len(graph_nodes) * 60, 600), 24000)
    graph_image: bytes = graph.get_png(image_height)
    with open(f"links-{layout_name}.png", "wb+") as png_file:
        png_file.write(graph_image)


def save_transition_matrix(index: Dict[str, int], matrix: DataFrame) -> None:
    log.info("Сохраняю матрицу переходов")
    reverted_index: Dict[int, str] = dict((url_index, url) for url, url_index in index.items())
    matrix.columns = list(reverted_index[url_index] for url_index in matrix.columns)
    matrix.index = list(reverted_index[url_index] for url_index in matrix.index)
    matrix.to_csv("matrix.csv")


if __name__ == '__main__':
    main()
