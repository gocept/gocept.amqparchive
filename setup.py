# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from setuptools import setup, find_packages


setup(
    name='gocept.amqparchive',
    version='0.1dev',
    author='gocept',
    author_email='mail@gocept.com',
    url='',
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
        'gocept.amqprun>0.3',
        'pyes',
        'setuptools',
        'zope.interface',
        'zope.component[zcml]',
    ],
    extras_require=dict(test=[
        'gocept.selenium',
        'mock',
        'zope.configuration',
        'zope.event',
    ]),
)
