# SPDX-FileCopyrightText: 2021 Forschungs- und Entwicklungszentrum Fachhochschule Kiel GmbH
# 
# SPDX-License-Identifier: GPL-3.0-or-later

import setuptools

with open('README.md') as readme:
    long_description = readme.read()

setuptools.setup(
    name='rogue',
    version='0.1.7',
    author="Forschungs- und Entwicklungszentrum Fachhochschule Kiel GmbH",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='GPL-3.0-or-later',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    python_requires='>=3.7',
)
