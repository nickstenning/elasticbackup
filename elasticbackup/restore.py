#!/usr/bin/env python

from __future__ import print_function

import argparse
import logging
import json

import elasticsearch

logging.basicConfig(format='%(asctime)s [%(name)s] [%(levelname)s] '
                           '%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

log_levels = [logging.WARN, logging.INFO, logging.DEBUG]
log = logging.getLogger('elasticbackup')
log_es = logging.getLogger('elasticsearch')

parser = argparse.ArgumentParser(
    'elasticrestore',
    description='Restore data and mappings to an ElasticSearch index')
parser.add_argument('host',
                    help='elasticsearch host')
parser.add_argument('index',
                    help='elasticsearch index name')
parser.add_argument('-m', '--mappings-file',
                    help='mappings output filename',
                    required=True)
parser.add_argument('-d', '--documents-file',
                    help='documents output filename',
                    required=True)
parser.add_argument('-b', '--batch-size',
                    help='document upload batch size',
                    type=int,
                    default=1000)
parser.add_argument('-v', '--verbose',
                    help='increase output verbosity',
                    action='count',
                    default=0)
parser.add_argument('-u', '--user',
                    help='HTTP auth (in format user:pass)')


def create_index(es, index, f):
    mappings = json.load(f)
    es.indices.create(index=index, body=mappings)


def create_documents(es, index, f, batch_size=1000):
    total = 0

    for size, batch in document_batches(f, batch_size):
        es.bulk(index=index, body=batch)
        total += size
        log.info("uploaded %s (total: %s)", size, total)


def document_batches(fp, batch_size):
    i = 0
    batch = []

    for line in fp:
        obj = json.loads(line)
        src = obj.pop('_source')
        batch.append(json.dumps({"create": obj}))
        batch.append(json.dumps(src))
        i += 1

        if i >= batch_size:
            yield i, batch
            i = 0
            batch = []

    if batch:
        yield i, batch


def main():
    args = parser.parse_args()

    verbose = min(args.verbose, 2)
    log.setLevel(log_levels[verbose])
    log_es.setLevel(log_levels[verbose])

    conn_kwargs = {}
    if args.user:
        conn_kwargs['http_auth'] = args.user
    es = elasticsearch.Elasticsearch([args.host], **conn_kwargs)

    with open(args.mappings_file) as f:
        create_index(es, args.index, f)

    with open(args.documents_file) as f:
        create_documents(es, args.index, f, batch_size=args.batch_size)

if __name__ == '__main__':
    main()
