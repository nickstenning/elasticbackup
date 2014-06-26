#!/usr/bin/env python

from __future__ import print_function

import argparse
import datetime
import logging
import json
import time

import elasticsearch

logging.basicConfig(format='%(asctime)s [%(name)s] [%(levelname)s] '
                           '%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

log_levels = [logging.WARN, logging.INFO, logging.DEBUG]
log = logging.getLogger('elasticbackup')
log_es = logging.getLogger('elasticsearch')

today = datetime.datetime.utcnow().strftime("%Y%m%d")
mappings_filename = "%%(index_name)s-mappings-%s.json" % today
documents_filename = "%%(index_name)s-documents-%s.json" % today

parser = argparse.ArgumentParser(
    'elasticbackup',
    description='Back up data and mappings from an ElasticSearch index')
parser.add_argument('host',
                    help='elasticsearch host')
parser.add_argument('index',
                    help='elasticsearch index name')
parser.add_argument('-m', '--mappings-file',
                    help='mappings output filename',
                    default=mappings_filename)
parser.add_argument('-d', '--documents-file',
                    help='documents output filename',
                    default=documents_filename)
parser.add_argument('-b', '--batch-size',
                    help='document download batch size',
                    type=int,
                    default=1000)
parser.add_argument('-q', '--query',
                    help='query to pass to elasticsearch')
parser.add_argument('-u', '--user',
                    help='HTTP auth (in format user:pass)')
parser.add_argument('-v', '--verbose',
                    help='increase output verbosity',
                    action='count',
                    default=0)


def write_mappings(es, index, f):
    mapping = es.indices.get_mapping(index)
    json.dump(mapping[index], f)


def write_documents(es, index, f, batch_size=1000, query=None):
    def _write_hits(results):
        hits = results['hits']['hits']
        if hits:
            for hit in hits:
                hit.pop('_index', None)
                hit.pop('_score', None)
                f.write("%s\n" % json.dumps(hit))
            return results['_scroll_id'], len(hits)
        else:
            return None, 0

    if query is None:
        query = {"query": {"match_all": {}}}

    status = "got batch of %s (total: %s)"

    results = es.search(index=index, body=query, scroll="10m", size=batch_size)
    scroll_id, num = _write_hits(results)
    total = num
    log.info(status, num, total)

    while scroll_id is not None:
        time.sleep(1)
        results = es.scroll(scroll_id=scroll_id, scroll='10m')
        scroll_id, num = _write_hits(results)
        total += num
        log.info(status, num, total)


def main():
    args = parser.parse_args()

    verbose = min(args.verbose, 2)
    log.setLevel(log_levels[verbose])
    log_es.setLevel(log_levels[verbose])

    conn_kwargs = {}
    if args.user:
        conn_kwargs['http_auth'] = args.user
    es = elasticsearch.Elasticsearch([args.host], **conn_kwargs)

    with open(args.mappings_file % {'index_name': args.index}, 'w') as f:
        write_mappings(es, args.index, f)

    with open(args.documents_file % {'index_name': args.index}, 'w') as f:
        write_documents(es,
                        args.index,
                        f,
                        batch_size=args.batch_size,
                        query=args.query)


if __name__ == '__main__':
    main()
