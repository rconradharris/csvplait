from setuptools import setup, find_packages
from setuptools.command.sdist import sdist

setup(
    name='csvplait',
    version='0.1',
    description='Interactive Tool for Manipulating CSV files',
    url='https://github.com/rconradharris/csvplait',
    license='MIT',
    author='Rick Harris',
    author_email='rconradharris@gmail.com',
    packages=find_packages(exclude=['tests', 'bin']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6'
    ],
    install_requires=['prettytable'],
    scripts=['bin/csvplait'])
