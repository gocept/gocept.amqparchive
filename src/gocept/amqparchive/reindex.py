# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from gocept.amqprun.writefiles import FileWriter
import Queue
import gocept.amqparchive.interfaces
import gocept.amqparchive.xml
import logging
import multiprocessing
import optparse
import os.path
import pyes
import time
import zope.component
import zope.xmlpickle


log = logging.getLogger(__name__)


def reindex_file(path, base):
    log.info(path)

    directory = os.path.dirname(path)
    filename = os.path.basename(path)
    basename, extension = os.path.splitext(filename)

    if not base.endswith('/'):
        base += '/'

    body = open(path, 'r').read()
    data = dict(
        path=path.replace('%s' % base, ''),
        data=gocept.amqparchive.xml.jsonify(body),
    )
    header_file = os.path.join(directory, FileWriter.header_filename(filename))
    header = zope.xmlpickle.loads(open(header_file).read())
    data.update(header.__dict__)

    elastic = zope.component.getUtility(
        gocept.amqparchive.interfaces.IElasticSearch)
    elastic.index(data, 'queue', 'message')


def collect_message_files(path):
    for (dirpath, dirnames, filenames) in os.walk(path):
        for f in filenames:
            f = os.path.join(dirpath, f)
            if not FileWriter.is_header_file(f):
                yield f
        for d in dirnames:
            collect_message_files(os.path.join(dirpath, d))


def reindex_directory(path):
    files = collect_message_files(path)
    for f in files:
        reindex_file(f, path)


def reindex_directory_parallel(path, jobs):
    queue = multiprocessing.JoinableQueue()
    done = multiprocessing.Event()
    collect = multiprocessing.Process(
        target=worker_collect_files, args=(queue, path))
    collect.start()

    workers = []
    for i in range(jobs):
        job = multiprocessing.Process(
            target=worker_reindex_file, args=(queue, done, path))
        job.start()
        workers.append(job)

    collect.join()
    done.set()
    queue.join()


def worker_collect_files(queue, path):
    files = collect_message_files(path)
    for f in files:
        queue.put(f)


def worker_reindex_file(queue, done, base):
    while True:
        try:
            f = queue.get(False)
        except Queue.Empty:
            if done.is_set():
                break
            else:
                log.debug('Waiting 1s for more work')
                time.sleep(1)
                continue

        reindex_file(f, base)
        queue.task_done()


def delete_index(name):
    elastic = zope.component.getUtility(
        gocept.amqparchive.interfaces.IElasticSearch)
    elastic.delete_index(name)


def main(argv=None):
    o = optparse.OptionParser(
        prog='reindex_directory',
        description='Read archived message files into elasticsearch index',
        usage='%prog [-d] [-jX] -h host:port directory')
    o.add_option(
        '-d', '--delete', action='store_true',
        help='delete index first')
    o.add_option(
        '-c', '--connection',
        help='hostname and port of the elasticsearch server')
    o.add_option(
        '-j', '--jobs', default='1',
        help='amount of worker processes')

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

    jobs = int(options.jobs)
    if jobs == 1:
        reindex_directory(arguments[0])
    else:
        reindex_directory_parallel(arguments[0], jobs)

