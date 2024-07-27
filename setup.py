import pathlib

from setuptools import setup, find_packages

setup(
    name="redis-key-analyzer",
    version="0.1.3",
    description="Redis Key Analyzer is a CLI tool for scanning and analyzing Redis database keys, providing insights into their distribution, type, memory usage, and TTL.",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    author="Ryan Kang",
    author_email="serious8builder@gmail.com",
    licenses=["Apache-2.0"],
    project_urls={
        "Source": "https://github.com/runnable38/redis-key-analyzer",
    },
    packages=find_packages("redis_key_analyzer"),
    package_dir={"": "redis_key_analyzer"},
    include_package_data=True,
    install_requires=[
        "click",
        "redis",
        "tqdm",
        "prettytable",
    ],
    entry_points={"console_scripts": ["rka = rka.cli:main"]},
    keywords=["redis", "pypi", "redis keys analyzer"],
    python_requires=">=3.9",
    package_data={},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Environment :: Console",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3.9",
    ],
)
