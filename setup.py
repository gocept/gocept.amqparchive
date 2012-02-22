# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from setuptools import setup, find_packages


setup(
    name='gocept.amqparchive',
    version='1.2.1',
    author='Wolfgang Schnerring <ws@gocept.com>, Christopher Grebs <christopher.grebs@native-instruments.de>',
    author_email='mail@gocept.com',
    url='https://code.gocept.com/hg/public/gocept.amqparchive',
    description="""\
Archiving, indexing and search for AMQP messages.
""",
    long_description=(
        open('README.txt').read()
        + '\n\n'
        + open('CHANGES.txt').read()),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='ZPL',
    namespace_packages=['gocept'],
    install_requires=[
        'gocept.amqprun>=0.6dev',
        'lxml',
        'pyes',
        'setuptools',
        'zope.interface',
        'zope.component[zcml]',
        'zope.xmlpickle',
    ],
    extras_require=dict(test=[
        'gocept.selenium',
        'mock',
        'zope.configuration',
        'zope.event',
    ]),
    entry_points=dict(console_scripts=[
        'reindex_directory=gocept.amqparchive.reindex:main',
    ]),
)
