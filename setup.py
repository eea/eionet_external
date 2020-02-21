from __future__ import absolute_import
import os
from setuptools import setup, find_packages

NAME = 'eionet_external'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(os.path.join(*PATH)).read().strip()

setup(name=NAME,
      version=VERSION,
      long_description_content_type="text/x-rst",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      description='Eionet external helper methods',
      classifiers=[],
      keywords='',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
)
