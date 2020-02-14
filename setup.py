from __future__ import absolute_import
import os
from setuptools import setup, find_packages

setup(
    name='eionet_external',
    version='1.0'
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
