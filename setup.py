#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 09:41:14 2024

@author: user272
"""

from setuptools import find_packages, setup
with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name="INflux_F library",
    version="1.0.0",
    description="Influx_F dependencies library.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.cern.ch/ColdJigDCS/coldjiglib2",
    author="Freddie Whitehead",
    author_email="ankush.mitra@cern.ch",
    packages=find_packages(),
    install_requires=['influxdb-client','pi-plates','spidev','rpi.gpio','pyserial','func_timeout'],
    extras_require={'uk':['grant','TC08','tenma','HYT','fs2012'],'ec':['HYT', 'grant', 'tenma']}
)