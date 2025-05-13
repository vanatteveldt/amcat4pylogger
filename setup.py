#!/usr/bin/env python

from distutils.core import setup

setup(
    name="amcat4pylogger",
    version="0.0.1",
    description="Python logging facility with AmCAT4 backend",
    author="Wouter van Atteveldt",
    author_email="wouter@vanatteveldt.com",
    packages=["amcat4pylogger"],
    include_package_data=False,
    zip_safe=False,
    keywords=["API", "text"],
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Topic :: Text Processing",
    ],
    install_requires=["amcat4py"],
    extras_require={"dev": ["twine"]},
)
