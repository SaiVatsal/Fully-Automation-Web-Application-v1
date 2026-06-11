from setuptools import setup, find_packages

setup(
    name="netreach",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.1",
        "httpx>=0.27",
        "yt-dlp>=2024.1",
        "snscrape>=0.7",
        "feedparser>=6.0",
        "duckduckgo-search>=6.0",
        "PyYAML>=6.0",
        "rich>=13.0",
    ],
    entry_points={
        "console_scripts": [
            "netreach=netreach.cli:cli",
        ],
    },
)
