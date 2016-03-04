from deliveryslack import __version__
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def open_file(fname):
    return open(os.path.join(os.path.dirname(__file__), fname))

setup(
    name='deliveryslack',
    version=__version__,
    author='Sam Rosenstein',
    author_email='smr277@cornell.edu',
    packages=['deliveryslack'],
    url='https://github.com/smr277/deliveryslack',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],
    description='Read in emails and track packages. Post package information onto slack',
    long_description=open_file('README.md').read(),
    zip_safe=True,
    entry_points = {
        'console_scripts': ['deliveryslack=deliveryslack.main:main'],
    }
)