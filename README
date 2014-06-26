elasticbackup
=============

elasticbackup is a set of two command-line tools,

    elasticbackup, and
    elasticrestore

that you can use to backup and restore data from ElasticSearch indices using
their scroll[1] and bulk[2] APIs.

installing
----------

elasticbackup is available on the Python Package Index, so you can just

    pip install elasticbackup

usage
-----

To backup the data from an index "foo" on a remote server, "es-1.mydomain.com",
that listens on port 9200, you can run

    elasticbackup es-1.mydomain.com:9200 foo

By default, this will create two files in your working directory. One contains a
JSON-serialisation of the index's mappings. The other contains a dump of the
documents in the index, serialised as JSON, one per line.

To restore these files to a local index, you might run

    elasticrestore -d <documents> -m <mappings> localhost:9200 myfoo

For more information and complete options allowed by elasticbackup and
elasticrestore, run

    elasticbackup -h
    elasticrestore -h

license
-------

elasticbackup is released under the terms of the MIT license, a copy of which
can be found in this distribution, in the LICENSE file.

[1]: http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/search-request-scroll.html
[2]: http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/docs-bulk.html
