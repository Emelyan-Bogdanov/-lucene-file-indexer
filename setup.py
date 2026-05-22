from setuptools import setup, find_packages

setup(
    name="lucene-file-indexer",
    version="1.0.0",
    description="Fast desktop file search with PyLucene and Tika",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "file-indexer=fileindexer.app:main",
        ],
    },
    install_requires=[
        "pylucene>=9.0.0",
        "tika>=2.0.0",
    ],
    python_requires=">=3.10",
)
