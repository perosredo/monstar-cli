#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="monstar-cli",
    version="0.0.1",
    description="GNOME display layout manager CLI",
    author="ps",
    author_email="petar@sredojevic.ca",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'monstar=monstar.cli:main',
        ],
    },
    install_requires=[
        'PyGObject',
    ],
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Systems Administration',
    ],
)