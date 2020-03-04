from enum import Enum
import random
from .logger import Protocol
import os
import re


class ImageType(Enum):
    Friend = "friend"
    Group = "group"


ImageRegex = {
    "group": r"(?<=\{)([0-9A-Z]{8})\-([0-9A-Z]{4})-([0-9A-Z]{4})-([0-9A-Z]{4})-([0-9A-Z]{12})(?=\}\..*?)",
    "friend": r"(?<=/)([0-9a-z]{8})\-([0-9a-z]{4})-([0-9a-z]{4})-([0-9a-z]{4})-([0-9a-z]{12})"
}


def get_matched_string(regex_result):
    if regex_result:
        return regex_result.string[slice(*regex_result.span())]


_windows_device_files = (
    "CON",
    "AUX",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "LPT1",
    "LPT2",
    "LPT3",
    "PRN",
    "NUL",
)
_filename_ascii_strip_re = re.compile(r"[^A-Za-z0-9_.-]")


# def randomRangedNumberString(length_range=(9,)):
#     length = random.choice(length_range)
#     return random.choice(range(10 ** (length - 1), int("9" * (length))))


def protocol_log(func):
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            Protocol.info(f"protocol method {func.__name__} was called")
            return result
        except Exception as e:
            Protocol.error(f"protocol method {func.__name__} raised a error: {e.__class__.__name__}")
            raise e

    return wrapper


def secure_filename(filename):
    """

    :param filename:
    :return:
    """
    if isinstance(filename, str):
        from unicodedata import normalize

        filename = normalize("NFKD", filename).encode("ascii", "ignore")
        filename = filename.decode("ascii")

    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")

    filename = \
        str(_filename_ascii_strip_re.sub("", "_".join(filename.split()))).strip("._")

    if (
            os.name == "nt" and filename and \
            filename.split(".")[0].upper() in _windows_device_files
    ):
        filename = "_" + filename

    return filename
