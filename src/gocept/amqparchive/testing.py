# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.amqparchive
import gocept.amqparchive.connection
import gocept.amqparchive.interfaces
import gocept.amqprun.testing
import gocept.selenium.base
import os
import plone.testing
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


class ElasticLayer(plone.testing.Layer):
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

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.process = self.start_elastic()
        self.wait_for_elastic_to_start()

    def start_elastic(self):
        self.logfile = 'elasticsearch-test.log'
        hostname = os.environ['ELASTIC_HOSTNAME']
        return subprocess.Popen([
                os.path.join(
                    os.environ['ELASTIC_HOME'], 'bin', 'elasticsearch'),
                '-f',
                '-D', 'es.path.data=' + os.path.join(self.tmpdir, 'data'),
                '-D', 'es.path.work=' + os.path.join(self.tmpdir, 'work'),
                '-D', 'es.path.logs=' + os.path.join(self.tmpdir, 'logs'),
                '-D', 'es.cluster.name=gocept.amqparchive.testing',
                '-D', 'es.http.port=' + hostname.split(':', 1)[-1],
                ], stdout=open(self.logfile, 'w'), stderr=subprocess.STDOUT)

    def wait_for_elastic_to_start(self):
        sys.stdout.write('\n    Starting elasticsearch server')
        sys.stdout.flush()
        start = time.time()

        while True:
            time.sleep(0.5)
            sys.stdout.write('.')
            sys.stdout.flush()

            with open(self.logfile, 'r') as f:
                contents = f.read()
                if 'started' in contents:
                    sys.stdout.write(' done.\n  ')
                    return

                if time.time() - start > self.START_TIMEOUT:
                    sys.stdout.write(' failed, log output follows:\n')
                    print contents
                    sys.stdout.flush()
                    raise SystemExit

    def stop_elastic(self):
        self.process.terminate()
        self.process.wait()

    def tearDown(self):
        self.stop_elastic()
        shutil.rmtree(self.tmpdir)

    def testSetUp(self):
        # XXX using the IElasticSearch utility would be nicer,
        # but the layer structure wreaks havoc on that plan at the moment
        elastic = pyes.ES(os.environ['ELASTIC_HOSTNAME'])
        try:
            elastic.delete_index('_all')
        except pyes.exceptions.ElasticSearchException:
            pass

ELASTIC_LAYER = ElasticLayer()


class SettingsLayer(plone.testing.Layer):
    """Loads our configure.zcml and provides ISettings useful for testing.
    """

    defaultBases = (plone.testing.zca.LAYER_CLEANUP,)

    def setUp(self):
        self['settings'] = {}
        self['settings'][
            'gocept.amqparchive.elastic_hostname'] = os.environ[
            'ELASTIC_HOSTNAME']
        self['settings'][
            'gocept.amqparchive.elastic_autorefresh'] = True
        zope.component.getSiteManager().registerUtility(
            self['settings'], provided=gocept.amqprun.interfaces.ISettings)

    def tearDown(self):
        zope.component.getSiteManager().unregisterUtility(
            self['settings'], provided=gocept.amqprun.interfaces.ISettings)

SETTINGS_LAYER = SettingsLayer()


ZCML_LAYER = plone.testing.zca.ZCMLSandbox(
    name='ZCMLSandbox', module=__name__,
    filename='configure.zcml', package=gocept.amqparchive,
    bases=(SETTINGS_LAYER,))


FUNCTIONAL_LAYER = plone.testing.Layer(
    name='FunctionaLayer', module=__name__,
    bases=(ZCML_LAYER, ELASTIC_LAYER))


# Note that we don't load configure here, this is provided by
# gocept.amqprun.testing.MainTestCase.make_config()
QUEUE_LAYER = plone.testing.Layer(
    name='QueueLayer', module=__name__,
    bases=(gocept.amqprun.testing.QUEUE_LAYER, ELASTIC_LAYER))


class NginxLayer(plone.testing.Layer):
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

    def setUp(self):
        self.nginx()

    def tearDown(self):
        self.nginx('-s', 'quit')

    def nginx(self, *args):
        subprocess.call(
            ['nginx', '-c', self.nginx_conf] + list(args),
            stdout=open('/dev/null', 'w'), stderr=subprocess.STDOUT)

NGINX_LAYER = NginxLayer()

JAVASCRIPT_LAYER = gocept.selenium.base.Layer(NGINX_LAYER)
ENDTOEND_LAYER = gocept.selenium.base.Layer(
    ELASTIC_LAYER, NGINX_LAYER, ZCML_LAYER)


class ElasticHelper(object):

    @property
    def elastic(self):
        return zope.component.getUtility(
            gocept.amqparchive.interfaces.IElasticSearch)


class TestCase(unittest.TestCase, ElasticHelper):

    layer = FUNCTIONAL_LAYER


class SeleniumTestCase(unittest.TestCase,
                       gocept.selenium.base.TestCase,
                       ElasticHelper):

    layer = JAVASCRIPT_LAYER
    level = 3

    def open(self, path):
        self.selenium.open('http://%s%s' % (NginxLayer.hostname, path))

    def eval(self, text):
        return self.selenium.getEval(
            "var window = selenium.browserbot.getCurrentWindow();\n"
            + text)
