#!/usr/bin/env python

"""
Usage: esrestore <elasticsearch host> <index name> <mapping.json> <documents.json>

  e.g. esrestore localhost:9200 posts posts_mapping_backup.json posts_docs_backup.json
"""

from __future__ import print_function

import datetime
import json
import os
import sys
import time

import requests


BATCH_SIZE = 1000
REQUESTS_CONF = {'verbose': sys.stderr} if os.environ.get('DEBUG') is not None else {}


def usage():
    print(__doc__.strip(), file=sys.stderr)


def create_index(host, index):
    requests.put("%s/%s" % (host, index), config=REQUESTS_CONF)


def create_mappings(host, index, f):
    mappings = json.load(f)
    for k, v in mappings.iteritems():
        data = json.dumps(v)
        r = requests.put("%s/%s/%s/_mapping" % (host, index, k),
                         data=data,
                         config=REQUESTS_CONF)
        r.raise_for_status()


def create_documents(host, index, f):

    def _create_batch(b):
        data = '\n'.join(b)
        r = requests.post("%s/%s/_bulk" % (host, index), data=data, config=REQUESTS_CONF)
        r.raise_for_status()

    total = 0

    for size, batch in document_batches(f):
        _create_batch(batch)
        total += size
        print("  uploaded %s (total: %s)" % (size, total), file=sys.stderr)

def document_batches(fp):
    i = 0
    batch = []

    for line in fp:
        obj = json.loads(line)
        src = obj.pop('_source')
        batch.append(json.dumps({"create": obj}))
        batch.append(json.dumps(src))
        i += 1

        if i >= BATCH_SIZE:
            yield i, batch
            i = 0
            batch = []

    if batch:
        yield i, batch


def main():
    try:
        _, host, index, mappings_filename, documents_filename = sys.argv
    except ValueError:
        usage()
        sys.exit(1)

    if not host.startswith('http://'):
        host = 'http://' + host

    create_index(host, index)

    with open(mappings_filename) as f:
        create_mappings(host, index, f)

    with open(documents_filename) as f:
        create_documents(host, index, f)

if __name__ == '__main__':
    main()
