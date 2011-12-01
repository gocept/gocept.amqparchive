==================
gocept.amqparchive
==================

This package is an add-on application for gocept.amqprun_ that provides
three features:

- **Archive** queue messages by writing them to the filesystesm
- **Index** those messages using ElasticSearch_
- **Search** for messages with a HTML/JavaScript GUI

.. _gocept.amqprun: http://pypi.python.org/pypi/gocept.amqprun/
.. _ElasticSearch: http://elasticsearch.org/

.. contents:: :depth: 1


Installation
============

``gocept.amqparchive`` requires an ElasticSearch server. To set up the archive
and index portion, add something like this to your ``gocept.amqprun``
configuration::

    <eventlog>...</eventlog>
    <amqp-server>...</amqp-server>
    <worker>
      amount 2
      component-configuration site.zcml
    </worker>
    <settings>
      gocept.amqparchive.elastic_hostname localhost:9200
    </settings>

and in site.zcml::

    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:amqp="http://namespaces.gocept.com/amqp">

      <include package="gocept.amqprun" />
      <include package="gocept.amqparchive" />

      <amqp:writefiles
        routing_key="key.one key.two key.three"
        queue_name="archive"
        directory="/path/to/archive"
        pattern="{routing_key}/{date}/{msgid}-{unique}.xml"
        />
    </configure>

The HTML/JavaScript GUI expects ``/elasticsearch`` to proxy to the ElasticSearch
server, and ``/messages`` to point to the archive directory
(``/path/to/archive`` in our example). Here's an nginx config snippet::

    http {
      upstream elasticsearch {
        server localhost:9200;
      }

      server {
        listen localhost:8080;

        location /search/ {
          alias /path/to/gocept.amqparchive.egg/gocept/amqparchive/browser/;
          index index.html;
        }

        location /elasticsearch/ {
          proxy_pass http://elasticsearch/;
        }

        location /messages/ {
          alias /path/to/archive/;
          autoindex on;
        }
    }


Development
===========

The source code is available in the mercurial repository at
https://code.gocept.com/hg/public/gocept.amqparchive

Please report any bugs you find at
https://projects.gocept.com/projects/projects/gocept-amqparchive/issues
