#!/bin/python
from distutils.core import setup

setup(
    name='PMCrawl',
    author="Gab0",
    version='0.8',
    packages=['pmccrawl'],
    license='GPLv2',
    long_description=open('README.md').read(),
    scripts=['pmcc']
)
