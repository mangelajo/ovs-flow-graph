#!/usr/bin/env python

import setuptools

setuptools.setup(
        name = 'ovsflowgraph',
        version = '0.1.0',
        description = 'Show OpenFlow tables as graphs, for ovs linux plugin',
        author = 'Miguel Angel Ajo Pelayo',
        author_email = 'miguelangel@ajo.es',
        url = 'https://github.com/mangelajo/ovflowgraph',
        packages = setuptools.find_packages(exclude = ['ez_setup']),
        include_package_data = True,
        zip_safe = False,
        entry_points = {
            'console_scripts': [
                'ovsflowgraph = ovsflowgraph.cmdline:main'
            ]},
        install_requires = ['jinja2','unittest2','twisted'],
        data_files = [],
        test_suite = 'ovsflowgraph.test.testcases'
        )



