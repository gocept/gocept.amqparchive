# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.amqparchive.reindex
import mock
import os.path
import pkg_resources
import unittest


class ReindexTest(unittest.TestCase):

    def test_reads_body_and_headers_from_file(self):
        with mock.patch('zope.component.getUtility') as getUtility:
            directory = pkg_resources.resource_filename(
                __name__, 'fixtures')
            gocept.amqparchive.reindex.reindex_file(
                os.path.join(directory, 'message.xml'), directory)
            elastic = getUtility()
        data = elastic.index.call_args[0][0]
        self.assertEqual('This is only a test.', data['data']['foo'])
        self.assertEqual('amqparchive', data['app_id'])
        self.assertEqual('message.xml', data['path'])

    def test_reindexes_each_message_filtering_out_header_files(self):
        files = gocept.amqparchive.reindex.collect_message_files(
            pkg_resources.resource_filename(__name__, 'fixtures'))
        self.assertEqual(1, len(list(files)))


# XXX tests for command line entry point are missing
