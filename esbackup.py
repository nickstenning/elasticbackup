#!/usr/bin/env python

"""
Usage: esbackup <elasticsearch host> <index name>

  e.g. esbackup localhost:9200 posts
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


def write_mappings(host, index, f):
    r = requests.get("%s/%s/_mapping" % (host, index), config=REQUESTS_CONF)
    obj = json.loads(r.content)
    json.dump(obj[obj.keys()[0]], f)


def write_documents(host, index, f):
    def _write_batch(scroll_id):
        time.sleep(1)
        r = requests.get("%s/_search/scroll?scroll=10m" % host, data=scroll_id, config=REQUESTS_CONF)
        obj = json.loads(r.content)

        hits = obj['hits']['hits']
        if hits:
            for hit in hits:
                hit.pop('_index', None)
                hit.pop('_score', None)
                f.write("%s\n" % json.dumps(hit))

            return obj['_scroll_id'], len(hits)
        else:
            return None, 0

    r = requests.get("%s/%s/_search?search_type=scan&scroll=10m&size=%s"
                     % (host, index, BATCH_SIZE),
                     data='{"query":{"match_all":{}}}',
                     config=REQUESTS_CONF)
    scroll_id = json.loads(r.content)['_scroll_id']

    total = 0
    while scroll_id is not None:
        scroll_id, num = _write_batch(scroll_id)
        total += num
        print("  got batch of %s (total: %s)" % (num, total), file=sys.stderr)


def main():
    try:
        _, host, index = sys.argv
    except ValueError:
        usage()
        sys.exit(1)

    today = datetime.datetime.utcnow().strftime("%Y%m%d")
    mappings_filename = "%s-mappings-%s.json" % (index, today)
    documents_filename = "%s-documents-%s.json" % (index, today)

    if not host.startswith('http://'):
        host = 'http://' + host

    with open(mappings_filename, 'w') as f:
        write_mappings(host, index, f)

    with open(documents_filename, 'w') as f:
        write_documents(host, index, f)

if __name__ == '__main__':
    main()
