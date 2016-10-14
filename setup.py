#!/usr/bin/env python

from setuptools import setup

with open('requirements.txt') as f:
  required = f.read().splitlines()

NAME = 'fldb'
VERSION = '0.0.1'

setup(**{
  'author': 'FarmLogs',
  'author_email': 'engineering@farmlogs.com',
  'download_url': 'https://github.com/FarmLogs/%s/tarball/%s' % (NAME, VERSION, ),
  'install_requires': required,
  'name': NAME,
  'py_modules': [NAME],
  'url': 'https://github.com/FarmLogs/%s' % NAME,
  'version': VERSION,
})
