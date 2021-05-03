import logging
from argparse import Namespace
from itertools import chain
from typing import Dict, List, Tuple

from pandas import DataFrame

from implementation.common import page_link_repository_name
from implementation.configuration import SafeArgumentParser
from implementation.infrastructure import get_logger
from implementation.page_link import PageLink, PageLinkRepository

log: logging.Logger = get_logger()


def main() -> None:
	configuration: Namespace = get_configuration()

	page_links: List[PageLink] = get_page_links(page_link_repository_name)

	page_ranks: Dict[str, float] = calculate_page_ranks(
		page_links,
		configuration.dumping_factor,
		configuration.iterations_count)

	save_page_ranks(page_ranks)


def get_configuration(unparsed_args: List[str] = None) -> Namespace:
	argument_parser: SafeArgumentParser = SafeArgumentParser()
	argument_parser.add_argument(
		"-df",
		type = float,
		help = "dumping factor",
		default = 0.9,
		dest = "dumping_factor")
	argument_parser.add_argument(
		"-ic",
		type = int,
		help = "iterations count",
		default = 20,
		dest = "iterations_count")
	return argument_parser.parse_args(unparsed_args)


def get_page_links(repository_name: str) -> List[PageLink]:
	log.info("Инициализирую хранилище ссылок " + repository_name)
	page_links_repository: PageLinkRepository = PageLinkRepository(repository_name)
	return page_links_repository.get_all()


def calculate_page_ranks(
		page_links: List[PageLink],
		damping_factor: float,
		iterations_count: int) -> Dict[str, float]:
	index, transition_matrix = build_transition_matrix(page_links)
	pages_count: int = len(index)

	log.info(
		f"Рассчитываю PageRank страниц в графе из {len(page_links)} ссылок "
		+ f"с damping factor {damping_factor} для {iterations_count} итераций")
	raise NotImplementedError()


def build_transition_matrix(page_links: List[PageLink]) -> Tuple[Dict[str, int], DataFrame]:
	log.info("Строю индекс")
	page_urls: List[str] = list(
		chain(
			(link.from_url for link in page_links),
			(link.to_url for link in page_links)))
	index: Dict[str, int] = dict()
	for url in page_urls:
		if url not in index:
			index[url] = len(index)
	del page_urls

	log.info("Строю матрицу переходов")
	empty_column: List[float] = [0.0] * len(index)
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

	return index, matrix


def save_page_ranks(page_ranks: Dict[str, float]):
	log.info(f"Сохраняю рассчитанный PageRank")
	raise NotImplementedError()


if __name__ == '__main__':
	main()
