#!/usr/bin/env python

from setuptools import setup

with open('requirements.txt') as f:
  install_requires = f.read().splitlines()

NAME = 'fldb'
VERSION = '1.0.0'

setup(**{
    'author': 'FarmLogs',
    'author_email': 'engineering@farmlogs.com',
    'download_url': 'https://github.com/FarmLogs/%s/tarball/%s' % (NAME, VERSION, ),
    'install_requires': install_requires,
    'name': NAME,
    'py_modules': [NAME],
    'url': 'https://github.com/FarmLogs/%s' % NAME,
    'version': VERSION,
})
