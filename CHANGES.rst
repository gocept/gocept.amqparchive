Changelog
=========

1.3.0.post1 (2018-11-27)
------------------------

- Fix PyPI page rendering.


1.3.0 (2018-09-19)
------------------

- Adapt the Selenium-1 tests to Webdriver.

- Update to current bootstrap.py.

- Improve forward compatibility with Python 3.

- Force `pyes < 0.17` for now.


1.2.7 (2015-01-28)
------------------

- Update to current `bootstrap.py`.

- Move repository to `bitbucket.org`_.

.. _`bitbucket.org` : https://bitbucket.org/gocept/gocept.amqparchive


1.2.6 (2014-02-17)
------------------

- Update to ElasticSearch 1.0 API.


1.2.5 (2014-02-14)
------------------

- Allow configuring multiple elasticsearch hosts.

- Fix bug in ``reindex_directory``: we need to index the path relativ to the
  base directory, not the full filename.

- Start reindexing in parallel while files are still being collected.


1.2.4 (2013-11-27)
------------------

- Add parallel worker mode to ``reindex_directory``.

- Handle invalid XML input (#10864).


1.2.3 (2012-04-18)
------------------

- Catch connection errors to ElasticSearch so they don't break the normal
  message handling. Messages that have not been index due to this can still be
  indexed later on via ``reindex_directory`` (#9363).


1.2.2 (2012-03-29)
------------------

- Make amqp server configurable for tests.


1.2.1 (2012-02-22)
------------------

- Switch to plone.testing.


1.2.0 (2011-08-23)
------------------

- Transform the XML body into a nested dict so ElasticSearch can index the
  fields individually.


1.1.0 (2011-08-23)
------------------

- Add command-line script ``reindex_directory``.


1.0.0 (2011-08-22)
------------------

- first release.
