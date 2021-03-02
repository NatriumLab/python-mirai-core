from setuptools import setup, find_packages
import pathlib
import re

WORK_DIR = pathlib.Path(__file__).parent

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

def get_version():
    """
    Read version
    :return: str
    """
    txt = (WORK_DIR / 'mirai_core' / '__init__.py').read_text('utf-8')
    try:
        return re.findall(r"^__VERSION__ = '(.*)'[\r\n]?$", txt, re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')

setup(
    name="python-mirai-core",
    version=get_version(),
    description='A framework for OICQ(QQ, made by Tencent) headless client "Mirai".',
    author='Chenwe-i-lin, jqqqqqqqqqq',
    author_email="Chenwe_i_lin@outlook.com",
    url="https://github.com/NatriumLab/python-mirai-core",
    packages=find_packages(include=("mirai_core", "mirai_core.*")),
    python_requires='>=3.7',
    keywords=["oicq qq qqbot", ],
    install_requires=[
        "aiohttp",
        "pydantic==1.7.3"
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: User Interfaces',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        "Operating System :: OS Independent"
    ]
)
