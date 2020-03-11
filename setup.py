from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python-mirai-core",
    version='0.6.4',
    description='A framework for OICQ(QQ, made by Tencent) headless client "Mirai".',
    author='Chenwe-i-lin, jqqqqqqqqqq',
    author_email="Chenwe_i_lin@outlook.com",
    url="https://github.com/NatriumLab/python-mirai-core",
    packages=find_packages(include=("mirai_core", "mirai_core.*")),
    python_requires='>=3.7',
    keywords=["oicq qq qqbot", ],
    install_requires=[
        "aiohttp",
        "pydantic"
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
