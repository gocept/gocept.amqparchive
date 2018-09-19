from setuptools import setup, find_packages


setup(
    name='gocept.amqparchive',
    version='1.3.0',
    author='Wolfgang Schnerring, Christopher Grebs',
    author_email='mail@gocept.com',
    url='https://bitbucket.org/gocept/gocept.amqparchive',
    description="""\
Archiving, indexing and search for AMQP messages.
""",
    long_description=(
        open('README.rst').read()
        + '\n\n'
        + open('CHANGES.rst').read()),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='ZPL',
    namespace_packages=['gocept'],
    install_requires=[
        'gocept.amqprun>=0.7.dev',
        'lxml',
        'pyes < 0.17',
        'setuptools',
        'zope.interface',
        'zope.component[zcml]',
        'zope.xmlpickle',
    ],
    extras_require=dict(test=[
        'gocept.amqprun [test]>=0.7.dev',
        'gocept.selenium',
        'gocept.testing',
        'mock',
        'zope.configuration',
        'zope.event',
    ]),
    entry_points=dict(console_scripts=[
        'reindex_directory=gocept.amqparchive.reindex:main',
    ]),
)
