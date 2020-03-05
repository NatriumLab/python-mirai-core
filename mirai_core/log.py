import sys

from logging import DEBUG, Formatter, getLogger, Logger, StreamHandler


logger = getLogger('Mirai-core')


def create_logger(module: str) -> Logger:
    """
    create logger for module
    """
    return logger.getChild(module)


def install_logger():
    default_handler = StreamHandler(sys.stderr)
    default_handler.setFormatter(Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
    logger.setLevel(DEBUG)
    logger.addHandler(default_handler)
