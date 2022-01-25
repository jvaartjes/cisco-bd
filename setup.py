#!/usr/bin/env python
"""The setup script"""
import os
import sys

from setuptools import find_packages, setup


def read(*parts):
    """Read file."""
    filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), *parts)
    sys.stdout.write(filename)
    with open(filename, encoding="utf-8", mode="rt") as fp:
        return fp.read()


with open("README.md", encoding="utf8") as readme_file:
    readme = readme_file.read()

setup(
    author="Jochem Vaartjes",
    author_email="jochem@jochem.me",
    version="0.1.2",
    classifiers=[
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    description="Asynchronous API client for Cisco Business Dashboard",
    include_package_data=True,
    install_requires=["sseclient<=0.0.23"],
    keywords=["cisco", "dashboard", "network", "api", "async", "client"],
    license="GNU General Public License (GPL)",
    long_description_content_type="text/markdown",
    long_description=readme,
    name="ciscobusinessdashboard",
    packages=find_packages(include=["ciscobusinessdashboard"]),
    url="https://github.com/jvaartjes/ciscobusinessdashboard",
    zip_safe=False,
)
