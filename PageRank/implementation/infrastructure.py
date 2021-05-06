import logging
import os
import sys
import traceback

from tinydb import TinyDB

database_file_name = "database.json"


def configure_logging():
	log_formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
	root_logger = logging.getLogger()
	root_logger.setLevel(logging.DEBUG)

	console_handler = logging.StreamHandler()
	console_handler.setFormatter(log_formatter)
	console_handler.setLevel(logging.INFO)
	root_logger.addHandler(console_handler)


def get_current_exception() -> BaseException:
	return sys.exc_info()[1]


def format_exception(exception):
	return os.linesep.join(traceback.format_exception_only(type(exception), exception))


def get_tinydb_table(database_file_path):
	return TinyDB(database_file_path, encoding = "utf-8", ensure_ascii = False, separators = (",", ":"))
