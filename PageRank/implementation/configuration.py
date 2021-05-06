from argparse import ArgumentParser

from implementation.infrastructure import get_current_exception


class SafeArgumentParser(ArgumentParser):
	def error(self, message) -> None:
		if get_current_exception() is not None:
			super().error(message)
