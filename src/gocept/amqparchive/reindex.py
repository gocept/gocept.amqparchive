# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from gocept.amqprun.writefiles import FileWriter
import gocept.amqparchive.interfaces
import gocept.amqparchive.xml
import logging
import optparse
import os.path
import pyes
import zope.component
import zope.xmlpickle


log = logging.getLogger(__name__)


def reindex_file(path):
    directory = os.path.dirname(path)
    filename = os.path.basename(path)
    basename, extension = os.path.splitext(filename)

    body = open(path, 'r').read()
    data = dict(
        path=path,
        data=gocept.amqparchive.xml.jsonify(body),
        )
    header_file = os.path.join(directory, FileWriter.header_filename(filename))
    header = zope.xmlpickle.loads(open(header_file).read())
    data.update(header.__dict__)

    elastic = zope.component.getUtility(
        gocept.amqparchive.interfaces.IElasticSearch)
    elastic.index(data, 'queue', 'message')


def reindex_directory(path):
    for (dirpath, dirnames, filenames) in os.walk(path):
        for f in filenames:
            f = os.path.join(dirpath, f)
            if not FileWriter.is_header_file(f):
                log.info(f)
                reindex_file(f)
        for d in dirnames:
            reindex_directory(os.path.join(dirpath, d))


def delete_index(name):
    elastic = zope.component.getUtility(
        gocept.amqparchive.interfaces.IElasticSearch)
    elastic.delete_index(name)


def main(argv=None):
    o = optparse.OptionParser(
        prog='reindex_directory',
        description='Read archived message files into elasticsearch index',
        usage='%prog [-d] -h host:port directory')
    o.add_option(
        '-d', '--delete', action='store_true',
        help='delete index first')
    o.add_option(
        '-c', '--connection',
        help='hostname and port of the elasticsearch server')

    options, arguments = o.parse_args(argv)
    if len(arguments) != 1:
        o.error('must specify a directory')

    if not options.connection:
        o.error('elasticsearch server name is required')

    logging.basicConfig(level=logging.ERROR, format='%(message)s')
    log.setLevel(logging.INFO)

    es = pyes.ES(options.connection)
    zope.component.provideUtility(
        es, gocept.amqparchive.interfaces.IElasticSearch)

    if options.delete:
        log.info('deleting index "queue"')
        delete_index('queue')

    reindex_directory(arguments[0])
