# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.amqparchive.connection
import gocept.amqparchive.interfaces
import gocept.amqprun
import os
import pyes.exceptions
import shutil
import subprocess
import sys
import tempfile
import time
import time
import unittest
import zope.component
import zope.component.testing


class ZCALayer(object):
    # XXX copy&paste from native.brave.connect

    @classmethod
    def setUp(cls):
        zope.component.testing.setUp()

    @classmethod
    def tearDown(cls):
        zope.component.testing.tearDown()

    @classmethod
    def testSetUp(cls):
        pass

    @classmethod
    def testTearDown(cls):
        pass


class SettingsLayer(ZCALayer):

    @classmethod
    def setUp(cls):
        cls.settings = {}
        zope.component.provideUtility(
            cls.settings, provides=gocept.amqprun.interfaces.ISettings)

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        pass

    @classmethod
    def testTearDown(cls):
        pass


class ElasticLayer(SettingsLayer):
    """Starts and stops an elasticsearch server and deletes all its indexes
    before each test is run.

    NOTE the following assumptions on the enclosing buildout:
    - the ${buildout:directory} is made available as os.environ['BUILDOUT_DIR']
    - the elasticsearch binary is available at
      ${buildout:directory}/elasticsearch/bin/elasticsearch


    The risk of targetting a production server with our "delete all indexes"
    operation is small: We terminate the test run when we can't start our own
    elastic server, e.g. when the port is already in use since a server is
    already running there.
    """

    hostname = 'localhost'
    port = '9212'
    START_TIMEOUT = 15

    @classmethod
    def setUp(cls):
        cls.tmpdir = tempfile.mkdtemp()

        cls.process = cls.start_elastic()
        cls.wait_for_elastic_to_start()

        SettingsLayer.settings[
            'gocept.amqparchive.elastic_hostname'] = '%s:%s' % (
            cls.hostname, cls.port)
        cls.elastic = gocept.amqparchive.connection.ElasticSearch()
        zope.component.provideUtility(
            cls.elastic, provides=gocept.amqparchive.interfaces.IElasticSearch)

    @classmethod
    def start_elastic(cls):
        elastic_home = os.path.join(
            os.environ['BUILDOUT_DIR'], 'parts', 'elasticsearch')
        cls.logfile = os.path.join(elastic_home, 'test.log')
        return subprocess.Popen([
                os.path.join(elastic_home, 'bin', 'elasticsearch'),
                '-f',
                '-D', 'es.path.data=' + os.path.join(cls.tmpdir, 'data'),
                '-D', 'es.path.work=' + os.path.join(cls.tmpdir, 'work'),
                '-D', 'es.http.port=' + cls.port,
                ], stdout=open(cls.logfile, 'w'), stderr=subprocess.STDOUT)

    @classmethod
    def wait_for_elastic_to_start(cls):
        sys.stdout.write('\n    Starting elasticsearch server')
        sys.stdout.flush()
        start = time.time()

        while True:
            time.sleep(0.5)
            sys.stdout.write('.')
            sys.stdout.flush()

            with open(cls.logfile, 'r') as f:
                contents = f.read()
                if 'started' in contents:
                    sys.stdout.write(' done.\n  ')
                    return

                if time.time() - start > cls.START_TIMEOUT:
                    sys.stdout.write(' failed, log output follows:\n')
                    print contents
                    sys.stdout.flush()
                    raise SystemExit

    @classmethod
    def stop_elastic(cls):
        cls.process.terminate()
        cls.process.wait()

    @classmethod
    def tearDown(cls):
        cls.stop_elastic()
        shutil.rmtree(cls.tmpdir)

    @classmethod
    def testSetUp(cls):
        try:
            cls.elastic.delete_index('_all')
        except pyes.exceptions.ElasticSearchException:
            pass

    @classmethod
    def testTearDown(cls):
        pass
