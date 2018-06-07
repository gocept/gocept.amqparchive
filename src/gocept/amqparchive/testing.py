import gocept.amqparchive
import gocept.amqparchive.interfaces
import gocept.amqprun.testing
import gocept.selenium.webdriver
import os
import plone.testing
import pyes.exceptions
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import zope.component


class ElasticLayer(plone.testing.Layer):
    """Start and stop an elasticsearch server.

    Delete all its indexes before each test is run.

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
        result = subprocess.Popen([
            os.path.join(
                os.environ['ELASTIC_HOME'], 'bin', 'elasticsearch'),
            '-f',
            # XXX our really old ES version has problems with java-1.7
            '-Xss256k',
            '-D', 'es.path.data=' + os.path.join(self.tmpdir, 'data'),
            '-D', 'es.path.work=' + os.path.join(self.tmpdir, 'work'),
            '-D', 'es.path.logs=' + os.path.join(self.tmpdir, 'logs'),
            '-D', 'es.cluster.name=gocept.amqparchive.testing',
            '-D', 'es.http.port=' + hostname.split(':', 1)[-1],
        ], stdout=open(self.logfile, 'w'), stderr=subprocess.STDOUT)
        return result

    def wait_for_elastic_to_start(self):
        sys.stdout.write('\n    Starting elasticsearch server')
        sys.stdout.flush()
        start = time.time()

        while True:
            sys.stdout.write('.')
            sys.stdout.flush()

            with open(self.logfile, 'r') as f:
                contents = f.read()
                if 'started' in contents:
                    sys.stdout.write(' done.\n  ')
                    return

                if time.time() - start > self.START_TIMEOUT:
                    sys.stdout.write(' failed, log output follows:\n')
                    print(contents)
                    sys.stdout.flush()
                    raise SystemExit
            time.sleep(1)

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
    """Load our configure.zcml and provides ISettings useful for testing."""

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
    debug = False

    def setUp(self):
        self.nginx()
        self['http_address'] = self.hostname

    def tearDown(self):
        self.nginx('-s', 'quit')
        del self['http_address']

    def nginx(self, *args):
        stdout = sys.stdout if self.debug else open('/dev/null', 'w')
        subprocess.call(
            ['nginx', '-c', self.nginx_conf] + list(args),
            stdout=stdout, stderr=subprocess.STDOUT,
            cwd=os.path.dirname(self.nginx_conf))


NGINX_LAYER = NginxLayer()


def WebdriverLayer(bases, name):
    """Webdriver layer based on other layer(s)."""
    webdriver = gocept.selenium.webdriver.Layer(
        bases=bases, name='{}Webdriver'.format(name), module=__name__)
    return gocept.selenium.webdriver.WebdriverSeleneseLayer(
        bases=[webdriver], name='{}WebdriverSelenese'.format(name),
        module=__name__)


JAVASCRIPT_LAYER = WebdriverLayer([NGINX_LAYER], 'JavaScript')
ENDTOEND_LAYER = WebdriverLayer(
    [ELASTIC_LAYER, NGINX_LAYER, ZCML_LAYER], 'EndToEnd')


class ElasticHelper(object):
    """Mix-in to ease getting the elastic search utility."""

    @property
    def elastic(self):
        return zope.component.getUtility(
            gocept.amqparchive.interfaces.IElasticSearch)


class TestCase(unittest.TestCase, ElasticHelper):
    """Default test case class."""

    layer = FUNCTIONAL_LAYER


class SeleniumTestCase(unittest.TestCase,
                       gocept.selenium.webdriver.WebdriverSeleneseTestCase,
                       ElasticHelper):
    """Test class for selenium tests."""

    layer = JAVASCRIPT_LAYER
    level = 3

    def open(self, path):
        self.selenium.open('http://%s%s' % (NginxLayer.hostname, path))

    def eval(self, text):
        return self.selenium.getEval(text)
