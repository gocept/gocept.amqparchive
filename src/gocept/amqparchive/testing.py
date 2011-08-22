# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.amqparchive
import gocept.amqparchive.connection
import gocept.amqparchive.interfaces
import gocept.amqprun.testing
import gocept.selenium.base
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
import zope.configuration.xmlconfig


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


class ElasticLayer(object):
    """Starts and stops an elasticsearch server and deletes all its indexes
    before each test is run.

    NOTE the following assumptions on the enclosing buildout:
    - the location of the elasticsearch distribution is in
      os.environ['ELASTIC_HOME']
      (i.e. the binary is at $ELASTIC_HOME/bin/elasticsearch
    - the hostname:port we should bind to is in os.environ['ELASTIC_HOSTNAME']

    The risk of targetting a production server with our "delete all indexes"
    operation is small: We terminate the test run when we can't start our own
    elastic server, e.g. when the port is already in use since a server is
    already running there.
    """

    START_TIMEOUT = 15

    @classmethod
    def setUp(cls):
        cls.tmpdir = tempfile.mkdtemp()
        cls.process = cls.start_elastic()
        cls.wait_for_elastic_to_start()

    @classmethod
    def start_elastic(cls):
        cls.logfile = 'elasticsearch-test.log'
        hostname = os.environ['ELASTIC_HOSTNAME']
        return subprocess.Popen([
                os.path.join(
                    os.environ['ELASTIC_HOME'], 'bin', 'elasticsearch'),
                '-f',
                '-D', 'es.path.data=' + os.path.join(cls.tmpdir, 'data'),
                '-D', 'es.path.work=' + os.path.join(cls.tmpdir, 'work'),
                '-D', 'es.path.logs=' + os.path.join(cls.tmpdir, 'logs'),
                '-D', 'es.cluster.name=gocept.amqparchive.testing',
                '-D', 'es.http.port=' + hostname.split(':', 1)[-1],
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
        # XXX using the IElasticSearch utility would be nicer,
        # but the layer structure wreaks havoc on that plan at the moment
        elastic = pyes.ES(os.environ['ELASTIC_HOSTNAME'])
        try:
            elastic.delete_index('_all')
        except pyes.exceptions.ElasticSearchException:
            pass

    @classmethod
    def testTearDown(cls):
        pass


class ZCMLLayer(ZCALayer):
    """Loads our configure.zcml and provides ISettings useful for testing.
    """

    @classmethod
    def setUp(cls):
        cls.settings = {}
        cls.settings[
            'gocept.amqparchive.elastic_hostname'] = os.environ[
            'ELASTIC_HOSTNAME']
        cls.settings[
            'gocept.amqparchive.elastic_autorefresh'] = True
        zope.component.provideUtility(
            cls.settings, provides=gocept.amqprun.interfaces.ISettings)

        zope.configuration.xmlconfig.file(
            'configure.zcml', gocept.amqparchive)

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        pass

    @classmethod
    def testTearDown(cls):
        pass


class FunctionalLayer(ZCMLLayer, ElasticLayer):

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        pass

    @classmethod
    def testTearDown(cls):
        pass


class QueueLayer(gocept.amqprun.testing.QueueLayer, ElasticLayer):
    """Combines QueueLayer and ElasticLayer.

    Note that we don't load configure here, this is provided by
    gocept.amqprun.testing.MainTestCase.make_config()
    """

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        pass

    @classmethod
    def testTearDown(cls):
        pass


class NginxLayer(object):
    """Starts and stops the nginx webserver.

    NOTE the following assumptions on the enclosing buildout:
    - nginx binary must be on the $PATH
    - a configuration file for nginx must be provided in the location given by
      os.envrion['NGINX_CONFIG']
    - the listening hostname:port in that configuration must be available in
      os.environ['NGINX_HOSTNAME'], so the tests know which server to target
    """

    nginx_conf = os.environ['NGINX_CONFIG']
    hostname = os.environ['NGINX_HOSTNAME']

    @classmethod
    def setUp(cls):
        cls.nginx()

    @classmethod
    def tearDown(cls):
        cls.nginx('-s', 'quit')

    @classmethod
    def nginx(cls, *args):
        subprocess.call(
            ['nginx', '-c', cls.nginx_conf] + list(args),
            stdout=open('/dev/null', 'w'), stderr=subprocess.STDOUT)

    @classmethod
    def testSetUp(cls):
        pass

    @classmethod
    def testTearDown(cls):
        pass


javascript_layer = gocept.selenium.base.Layer(NginxLayer)
endtoend_layer = gocept.selenium.base.Layer(
    ElasticLayer, NginxLayer, ZCMLLayer)


class ElasticHelper(object):

    @property
    def elastic(self):
        return zope.component.getUtility(
            gocept.amqparchive.interfaces.IElasticSearch)


class TestCase(unittest.TestCase, ElasticHelper):

    layer = FunctionalLayer


class SeleniumTestCase(unittest.TestCase,
                       gocept.selenium.base.TestCase,
                       ElasticHelper):

    layer = javascript_layer
    level = 3

    def open(self, path):
        self.selenium.open('http://%s%s' % (NginxLayer.hostname, path))

    def eval(self, text):
        return self.selenium.getEval(
            "var window = selenium.browserbot.getCurrentWindow();\n"
            + text)
