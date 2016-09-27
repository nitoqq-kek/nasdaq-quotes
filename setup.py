from distutils.core import setup
from setuptools import find_packages

setup(
    name='nasdaq-quotes',
    version='0.0.1',
    description='Tools for parse quotes from nasdaq.com and web API',
    author='Nikolay Konovalov',
    author_email='konovalov.nikolai@gmail.com',
    license='proprietary',
    packages=find_packages()
)
