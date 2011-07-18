# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from pyes.exceptions import ElasticSearchException
import gocept.amqparchive.testing


class ConnectionIntegrationTest(gocept.amqparchive.testing.TestCase):

    def test_aaa_index_and_retrieve_something(self):
        self.elastic.index(
            dict(foo='bar', qux='baz'), 'test-index', 'test-type', id=1)
        doc = self.elastic.get('test-index', 'test-type', 1)
        self.assertEqual('bar', doc['_source']['foo'])

    def test_bbb_index_from_other_tests_are_isolated(self):
        self.assertRaises(
            ElasticSearchException,
            lambda: self.elastic.get('test-index', 'test-type', 1))
