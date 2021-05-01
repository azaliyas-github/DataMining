import logging
import sys
from itertools import chain
from typing import Dict, List, Set, Tuple
from urllib.parse import ParseResult, urlparse

from pandas import DataFrame
from py2cytoscape.data.cynetwork import CyNetwork
from py2cytoscape.data.cyrest_client import CyRestClient

from implementation.common import page_link_repository_name
from implementation.infrastructure import configure_logging
from implementation.page_link import PageLink, PageLinkRepository

log: logging.Logger = logging.getLogger()


def main() -> None:
    layout_name: str = get_layout_name()

    configure_logging()

    page_links: List[PageLink] = get_page_links(page_link_repository_name)

    output_transition_matrix(page_links)
    draw_graph(page_links, layout_name)


def get_layout_name() -> str:
    if len(sys.argv) == 2:
        return sys.argv[1]

    return input("Layout: ")


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


def output_transition_matrix(page_links: List[PageLink]):
    page_urls: List[str] = list(
        chain(
            (link.from_url for link in page_links),
            (link.to_url for link in page_links)))
    index: Dict[str, int] = dict()
    for url in page_urls:
        if url not in index:
            index[url] = len(index)

    log.info("Строю индекс")
    index_csv: DataFrame = DataFrame(data = {"url": index.keys()}, index = index.values())

    log.info("Сохраняю индекс")
    index_csv.to_csv("index.csv", index_label = "id")
    del index_csv

    log.info("Строю матрицу переходов")
    empty_column: List[float] = [0.0] * len(page_urls)
    matrix: DataFrame = DataFrame(
        data = dict((id_, empty_column) for id_ in index.values()),
        dtype = float)
    for link in page_links:
        from_url_index: int = index[link.from_url]
        to_url_index: int = index[link.to_url]
        matrix.at[to_url_index, from_url_index] = float(link.count)
    for column in matrix.columns:
        column_sum: float = matrix[column].sum()
        if column_sum > 0:
            matrix[column] = matrix[column] / column_sum

    log.info("Сохраняю матрицу переходов")
    matrix.to_csv("matrix.csv")
    del matrix


if __name__ == '__main__':
    main()
