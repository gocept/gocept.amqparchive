# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from pyes.exceptions import ElasticSearchException
import gocept.amqparchive.interfaces
import gocept.amqparchive.testing
import time
import unittest
import zope.component


class ConnectionIntegrationTest(unittest.TestCase):

    level = 2
    layer = gocept.amqparchive.testing.ElasticLayer

    @property
    def elastic(self):
        return zope.component.getUtility(
            gocept.amqparchive.interfaces.IElasticSearch)

    def test_aaa_index_and_retrieve_something(self):
        self.elastic.index(
            dict(foo='bar', qux='baz'), 'test-index', 'test-type', id=1)
        time.sleep(1) # XXX why?
        doc = self.elastic.get('test-index', 'test-type', 1)
        self.assertEqual('bar', doc['_source']['foo'])

    def test_bbb_index_from_other_tests_are_isolated(self):
        self.assertRaises(
            ElasticSearchException,
            lambda: self.elastic.get('test-index', 'test-type', 1))