# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

from setuptools import setup, find_packages

setup(
    name="hintzcompiler",
    version="0.1",
    packages=find_packages(where="."),
    install_requires=[
        "lark",
    ],
    entry_points={
        "console_scripts": [
            "hintz=hintzCompiler.compiler:main"
        ]
    },
    python_requires=">=3.7",
)
