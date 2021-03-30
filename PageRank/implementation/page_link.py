from pathlib import Path

from implementation.infrastructure import get_tinydb_table


class PageLink:
	def __init__(self, depth, from_url, to_url):
		self.depth = depth
		self.from_url = from_url
		self.to_url = to_url


class PageLinkRepository:
	def __init__(self, name = ""):
		name = name if len(name) > 0 else "default"
		repository_path = Path(name)  # папка для хранилища имеет то же название, что и само хранилище

		repository_path.mkdir(parents = True, exist_ok = True)  # создаём папку для хранилища
		self.__table = get_tinydb_table(repository_path.joinpath("links.json"))  # создаём БД в файле links.json

	def get_all(self):
		return [self.__to_model(dbo) for dbo in self.__table.all()]

	def create(self, link):
		self.__table.insert(self.__to_dbo(link))

	def delete_all(self):
		self.__table.truncate()

	@staticmethod
	def __to_dbo(model):
		return dict(vars(model))

	@staticmethod
	def __to_model(dbo):
		model = object.__new__(PageLink)
		vars(model).update(dbo)
		return model
