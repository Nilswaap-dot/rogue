# SPDX-FileCopyrightText: 2021 Forschungs- und Entwicklungszentrum Fachhochschule Kiel GmbH
# 
# SPDX-License-Identifier: CC0-1.0

import setuptools

with open('README.md') as readme:
    long_description = readme.read()

setuptools.setup(
    name='rogue',
    version='0.1.7',
    author='M. Kliemann',
    author_email='mail@maltekliemann.com',
    description='IO hardware simulator',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='GPL v3.0',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    python_requires='>=3.7',
)
