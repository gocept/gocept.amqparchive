# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import gocept.amqparchive.archive
import gocept.amqparchive.testing
import gocept.amqprun.interfaces
import gocept.amqprun.testing
import os
import shutil
import tempfile
import time
import zope.event


class IndexTest(gocept.amqparchive.testing.TestCase):

    def create_message(self, body='<foo>testbody</foo>'):
        from gocept.amqprun.message import Message
        message = Message({}, body, routing_key='routing')
        message.header.message_id = 'myid'
        message.header.timestamp = time.mktime(
            datetime.datetime(2011, 7, 14, 14, 15).timetuple())
        return message

    def test_indexes_body_and_headers(self):
        message = self.create_message()
        zope.event.notify(gocept.amqprun.interfaces.MessageStored(
                message, '/foo/bar'))
        time.sleep(1) # give elasticsearch time to settle
        result = self.elastic.search({'query': {'text': {'_all': 'foo'}}})
        hits = result['hits']
        self.assertEqual(1, hits['total'])
        item = hits['hits'][0]['_source']
        self.assertEqual('/foo/bar', item['path'])
        self.assertEqual('testbody', item['data']['foo'])
        self.assertEqual('myid', item['message_id'])


class IndexIntegrationTest(gocept.amqprun.testing.MainTestCase,
                           gocept.amqparchive.testing.ElasticHelper):

    level = 3
    layer = gocept.amqparchive.testing.QUEUE_LAYER

    def setUp(self):
        super(IndexIntegrationTest, self).setUp()
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        super(IndexIntegrationTest, self).tearDown()

    def test_message_should_be_indexed(self):
        self.make_config(__name__, 'index', mapping=dict(
                routing_key='test.data',
                directory=self.tmpdir,
                queue_name=self.get_queue_name('test'),
                pattern='foo/bar/baz.xml',
                elastic_hostname=os.environ['ELASTIC_HOSTNAME']))
        self.create_reader()

        body = '<foo>This is only a test.</foo>'
        self.send_message(body, routing_key='test.data')
        for i in range(100):
            if not self.loop.tasks.qsize():
                break
            time.sleep(0.05)
        else:
            self.fail('Message was not processed.')

        self.assertEqual(
            2, len(os.listdir(os.path.join(self.tmpdir, 'foo', 'bar'))))
        # we're concurrent to the handler and we seem to be too fast
        time.sleep(2)
        result = self.elastic.search({'query': {'text': {'_all': 'only'}}})
        self.assertEqual(1, result['hits']['total'])
        hit = result['hits']['hits'][0]
        self.assertEqual('foo/bar/baz.xml', hit['_source']['path'])
