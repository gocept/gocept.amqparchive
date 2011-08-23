# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.amqparchive.reindex
import mock
import pkg_resources
import unittest


class ReindexTest(unittest.TestCase):

    def test_reads_body_and_headers_from_file(self):
        with mock.patch('zope.component.getUtility') as getUtility:
            gocept.amqparchive.reindex.reindex_file(
                pkg_resources.resource_filename(
                    __name__, 'fixtures/message.xml'))
            elastic = getUtility()
        data = elastic.index.call_args[0][0]
        self.assertEqual('This is only a test.', data['data']['foo'])
        self.assertEqual('amqparchive', data['app_id'])

    def test_reindexes_each_message_filtering_out_header_files(self):
        with mock.patch('gocept.amqparchive.reindex.reindex_file') as reindex:
            gocept.amqparchive.reindex.reindex_directory(
                pkg_resources.resource_filename(__name__, 'fixtures'))
            self.assertEqual(1, reindex.call_count)


# XXX tests for command line entry point are missing
