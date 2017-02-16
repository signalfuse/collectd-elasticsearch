#! /usr/bin/python
# Copyright 2014 Jeremy Carroll
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import collections
import json
import urllib2
import base64
import logging

PREFIX = "elasticsearch"
ES_HOST = "localhost"
ES_PORT = 9200
ES_CLUSTER = None
ES_USERNAME = ""
ES_PASSWORD = ""
ES_VERSION = None
ES_MASTER_ELIGIBLE = None

ENABLE_INDEX_STATS = True
ENABLE_CLUSTER_STATS = True

ES_NODE_URL = ""
ES_CLUSTER_URL = ""
ES_INDEX_URL = ""
ES_INDEX = []

Stat = collections.namedtuple('Stat', ('type', 'path'))

NODE_STATS_CUR = {}
INDEX_STATS_CUR = {}
CLUSTER_STATS_CUR = {}

COLLECTION_INTERVAL = 10

INDEX_INTERVAL = 300

INDEX_SKIP = 0

SKIP_COUNT = 0

CLUSTER_STATUS = {'green': 0, 'yellow': 1, 'red': 2}

DETAILED_METRICS = True
THREAD_POOLS = []
CONFIGURED_THREAD_POOLS = set()

ES_CURRENT_MASTER = False
MASTER_ONLY = False
NODE_ID = None

DEFAULTS = set([
    # AUTOMATICALLY GENERATED METRIC NAMES
    # TO INCLUDE BY DEFAULT
    "indices.total.docs.deleted",
    "indices.total.fielddata.memory-size",
    "indices.merges.total",
    "cluster.number-of-nodes",
    "process.open_file_descriptors",
    "indices.total.merges.total",
    "indices.total.store.size",
    "indices.segments.count",
    "indices.merges.current",
    "jvm.mem.heap-used",
    "indices.search.query-time",
    "cluster.number-of-data_nodes",
    "cluster.active-shards",
    "indices.indexing.index-total",
    "indices.get.total",
    "cluster.unassigned-shards",
    "indices.cache.field.size",
    "jvm.gc.time",
    "indices.store.size",
    "thread_pool.get.rejected",
    "indices.total.search.query-time",
    "indices.search.query-total",
    "indices.total.merges.total-time",
    "cluster.active-primary-shards",
    "indices.docs.deleted",
    "indices.cache.filter.size",
    "indices.total.search.query-total",
    "indices.docs.count",
    "indices.total.indexing.index-time",
    "indices.total.indexing.index-total",
    "jvm.mem.heap-committed",
    "indices.total.docs.count",
    "cluster.relocating-shards",
    "thread_pool.rejected",
    "jvm.uptime",
    "indices.total.filter-cache.memory-size",
])

DEFAULTS.update([
    # ADD ADDITIONAL METRIC NAMES
    # TO INCLUDE BY DEFAULT
    "cluster.status",
    "indices.indexing.index-time",
    "indices.merges.time",
    "indices.store.throttle-time",
])

# DICT: ElasticSearch 1.0.0
NODE_STATS = {
    # STORE
    'indices.store.throttle-time':
        Stat("counter", "nodes.%s.indices.store.throttle_time_in_millis"),

    # SEARCH
    'indices.search.open-contexts':
        Stat("gauge", "nodes.%s.indices.search.open_contexts"),

    # CACHE
    'indices.cache.field.eviction':
        Stat("counter", "nodes.%s.indices.fielddata.evictions"),
    'indices.cache.field.size':
        Stat("gauge", "nodes.%s.indices.fielddata.memory_size_in_bytes"),
    'indices.cache.filter.evictions':
        Stat("counter", "nodes.%s.indices.filter_cache.evictions"),
    'indices.cache.filter.size':
        Stat("gauge", "nodes.%s.indices.filter_cache.memory_size_in_bytes"),

    # GC
    'jvm.gc.time':
        Stat("counter",
             "nodes.%s.jvm.gc.collectors.young.collection_time_in_millis"),
    'jvm.gc.count':
        Stat("counter", "nodes.%s.jvm.gc.collectors.young.collection_count"),
    'jvm.gc.old-time':
        Stat("counter",
             "nodes.%s.jvm.gc.collectors.old.collection_time_in_millis"),
    'jvm.gc.old-count':
        Stat("counter", "nodes.%s.jvm.gc.collectors.old.collection_count"),

    # FLUSH
    'indices.flush.total':
        Stat("counter", "nodes.%s.indices.flush.total"),
    'indices.flush.time':
        Stat("counter", "nodes.%s.indices.flush.total_time_in_millis"),

    # MERGES
    'indices.merges.current':
        Stat("gauge", "nodes.%s.indices.merges.current"),
    'indices.merges.current-docs':
        Stat("gauge", "nodes.%s.indices.merges.current_docs"),
    'indices.merges.current-size':
        Stat("gauge", "nodes.%s.indices.merges.current_size_in_bytes"),
    'indices.merges.total':
        Stat("counter", "nodes.%s.indices.merges.total"),
    'indices.merges.total-docs':
        Stat("gauge", "nodes.%s.indices.merges.total_docs"),
    'indices.merges.total-size':
        Stat("counter", "nodes.%s.indices.merges.total_size_in_bytes"),
    'indices.merges.time':
        Stat("counter", "nodes.%s.indices.merges.total_time_in_millis"),

    # REFRESH
    'indices.refresh.total':
        Stat("counter", "nodes.%s.indices.refresh.total"),
    'indices.refresh.time':
        Stat("counter", "nodes.%s.indices.refresh.total_time_in_millis"),

    # SEGMENTS
    'indices.segments.count':
        Stat("gauge", "nodes.%s.indices.segments.count"),
    'indices.segments.size':
        Stat("gauge", "nodes.%s.indices.segments.memory_in_bytes"),
    'indices.segments.index-writer-max-size':
        Stat("gauge",
             "nodes.%s.indices.segments.index_writer_max_memory_in_bytes"),
    'indices.segments.index-writer-size':
        Stat("gauge",
             "nodes.%s.indices.segments.index_writer_memory_in_bytes"),

    # DOCS
    'indices.docs.count':
        Stat("gauge", "nodes.%s.indices.docs.count"),
    'indices.docs.deleted':
        Stat("gauge", "nodes.%s.indices.docs.deleted"),

    # STORE
    'indices.store.size':
        Stat("gauge", "nodes.%s.indices.store.size_in_bytes"),

    # INDEXING
    'indices.indexing.index-total':
        Stat("counter", "nodes.%s.indices.indexing.index_total"),
    'indices.indexing.index-time':
        Stat("counter", "nodes.%s.indices.indexing.index_time_in_millis"),
    'indices.indexing.delete-total':
        Stat("counter", "nodes.%s.indices.indexing.delete_total"),
    'indices.indexing.delete-time':
        Stat("counter", "nodes.%s.indices.indexing.delete_time_in_millis"),
    'indices.indexing.index-current':
        Stat("gauge", "nodes.%s.indices.indexing.index_current"),
    'indices.indexing.delete-current':
        Stat("gauge", "nodes.%s.indices.indexing.delete_current"),

    # GET
    'indices.get.total':
        Stat("counter", "nodes.%s.indices.get.total"),
    'indices.get.time':
        Stat("counter", "nodes.%s.indices.get.time_in_millis"),
    'indices.get.exists-total':
        Stat("counter", "nodes.%s.indices.get.exists_total"),
    'indices.get.exists-time':
        Stat("counter", "nodes.%s.indices.get.exists_time_in_millis"),
    'indices.get.missing-total':
        Stat("counter", "nodes.%s.indices.get.missing_total"),
    'indices.get.missing-time':
        Stat("counter", "nodes.%s.indices.get.missing_time_in_millis"),
    'indices.get.current':
        Stat("gauge", "nodes.%s.indices.get.current"),

    # SEARCH
    'indices.search.query-current':
        Stat("gauge", "nodes.%s.indices.search.query_current"),
    'indices.search.query-total':
        Stat("counter", "nodes.%s.indices.search.query_total"),
    'indices.search.query-time':
        Stat("counter", "nodes.%s.indices.search.query_time_in_millis"),
    'indices.search.fetch-current':
        Stat("gauge", "nodes.%s.indices.search.fetch_current"),
    'indices.search.fetch-total':
        Stat("counter", "nodes.%s.indices.search.fetch_total"),
    'indices.search.fetch-time':
        Stat("counter", "nodes.%s.indices.search.fetch_time_in_millis"),

    # JVM METRICS #
    # MEM
    'jvm.mem.heap-committed':
        Stat("gauge", "nodes.%s.jvm.mem.heap_committed_in_bytes"),
    'jvm.mem.heap-used':
        Stat("gauge", "nodes.%s.jvm.mem.heap_used_in_bytes"),
    'jvm.mem.heap-used-percent':
        Stat("percent", "nodes.%s.jvm.mem.heap_used_percent"),
    'jvm.mem.non-heap-committed':
        Stat("gauge", "nodes.%s.jvm.mem.non_heap_committed_in_bytes"),
    'jvm.mem.non-heap-used':
        Stat("gauge", "nodes.%s.jvm.mem.non_heap_used_in_bytes"),
    'jvm.mem.pools.young.max_in_bytes':
        Stat("gauge", "nodes.%s.jvm.mem.pools.young.max_in_bytes"),
    'jvm.mem.pools.young.used_in_bytes':
        Stat("gauge", "nodes.%s.jvm.mem.pools.young.used_in_bytes"),
    'jvm.mem.pools.old.max_in_bytes':
        Stat("gauge", "nodes.%s.jvm.mem.pools.old.max_in_bytes"),
    'jvm.mem.pools.old.used_in_bytes':
        Stat("gauge", "nodes.%s.jvm.mem.pools.old.used_in_bytes"),

    # UPTIME
    'jvm.uptime':
        Stat("counter", "nodes.%s.jvm.uptime_in_millis"),

    # THREADS
    'jvm.threads.count':
        Stat("gauge", "nodes.%s.jvm.threads.count"),
    'jvm.threads.peak':
        Stat("gauge", "nodes.%s.jvm.threads.peak_count"),

    # TRANSPORT METRICS #
    'transport.server_open':
        Stat("gauge", "nodes.%s.transport.server_open"),
    'transport.rx.count':
        Stat("counter", "nodes.%s.transport.rx_count"),
    'transport.rx.size':
        Stat("counter", "nodes.%s.transport.rx_size_in_bytes"),
    'transport.tx.count':
        Stat("counter", "nodes.%s.transport.tx_count"),
    'transport.tx.size':
        Stat("counter", "nodes.%s.transport.tx_size_in_bytes"),

    # HTTP METRICS #
    'http.current_open':
        Stat("gauge", "nodes.%s.http.current_open"),
    'http.total_open':
        Stat("counter", "nodes.%s.http.total_opened"),

    # PROCESS METRICS #
    'process.open_file_descriptors':
        Stat("gauge", "nodes.%s.process.open_file_descriptors"),
    'process.cpu.percent':
        Stat("gauge", "nodes.%s.process.cpu.percent"),
    'process.mem.share_in_bytes':
        Stat("gauge", "nodes.%s.process.mem.share_in_bytes"),
}

# Deprecated node stats by first version in which they were removed
DEPRECATED_NODE_STATS = [
    {
        'major': 2,
        'minor': 0,
        'revision': 0,
        'keys': ['process.mem.share_in_bytes'],
    },
    {
        'major': 5,
        'minor': 0,
        'revision': 0,
        'keys': ['indices.segments.index-writer-max-size']
    }
]

# Deprecated thread pools by first version in which they were removed
DEPRECATED_THREAD_POOLS = [
    {
        'major': 2,
        'minor': 0,
        'revision': 0,
        'keys': ['merge', 'optimize']
    },
    {
        'major': 5,
        'minor': 0,
        'revision': 0,
        'keys': ['suggest', 'percolate']
    }
]

NODE_STATS_ES_2 = {
    'indices.cache.filter.evictions':
        Stat("counter", "nodes.%s.indices.query_cache.evictions"),
    'indices.cache.filter.size':
        Stat("gauge", "nodes.%s.indices.query_cache.cache_size"),
    'indices.cache.filter.hit-count':
        Stat("counter", "nodes.%s.indices.query_cache.hit_count"),
    'indices.cache.filter.miss-count':
        Stat("counter", "nodes.%s.indices.query_cache.miss_count"),
    'indices.cache.filter.cache-count':
        Stat("counter", "nodes.%s.indices.query_cache.cache_count"),
    'indices.cache.filter.total-count':
        Stat("counter", "nodes.%s.indices.query_cache.total_count"),
    'indices.search.scroll-time':
        Stat("counter", "nodes.%s.indices.search.scroll_time_in_millis"),
    'indices.search.scroll.total':
        Stat("counter", "nodes.%s.indices.search.scroll_total"),
    'indices.search.scroll.current':
        Stat("gauge", "nodes.%s.indices.search.scroll_current"),
}

# ElasticSearch 1.3.0
INDEX_STATS_ES_1_3 = {
    # SEGMENTS
    "indices[index={index_name}].primaries.segments.index-writer-memory":
        Stat("gauge", "primaries.segments.index_writer_memory_in_bytes"),
    "indices[index={index_name}].primaries.segments.version-map-memory":
        Stat("gauge", "primaries.segments.version_map_memory_in_bytes"),
}

# ElasticSearch 1.1.0
INDEX_STATS_ES_1_1 = {
    # SUGGEST
    "indices[index={index_name}].primaries.suggest.total":
        Stat("counter", "primaries.suggest.total"),
    "indices[index={index_name}].primaries.suggest.time":
        Stat("counter", "primaries.suggest.time_in_millis"),
    "indices[index={index_name}].primaries.suggest.current":
        Stat("gauge", "primaries.suggest.current"),
}

# ElasticSearch 1.0.0
INDEX_STATS = {
    # PRIMARIES
    # TRANSLOG
    "indices[index={index_name}].primaries.translog.size":
        Stat("gauge", "primaries.translog.size_in_bytes"),
    "indices[index={index_name}].primaries.translog.operations":
        Stat("counter", "primaries.translog.operations"),

    # SEGMENTS
    "indices[index={index_name}].primaries.segments.memory":
        Stat("gauge", "primaries.segments.memory_in_bytes"),
    "indices[index={index_name}].primaries.segments.count":
        Stat("counter", "primaries.segments.count"),

    # ID_CACHE
    "indices[index={index_name}].primaries.id-cache.memory-size":
        Stat("gauge", "primaries.id_cache.memory_size_in_bytes"),

    # FLUSH
    "indices[index={index_name}].primaries.flush.total":
        Stat("counter", "primaries.flush.total"),
    "indices[index={index_name}].primaries.flush.total-time":
        Stat("counter", "primaries.flush.total_time_in_millis"),

    # WARMER
    "indices[index={index_name}].primaries.warmer.total.primaries.warmer"
    ".total-time": Stat(
        "counter", "primaries.warmer.total_time_in_millis"),
    "indices[index={index_name}].primaries.warmer.total":
        Stat("counter", "primaries.warmer.total"),
    "indices[index={index_name}].primaries.warmer.current":
        Stat("gauge", "primaries.warmer.current"),

    # FIELDDATA
    "indices[index={index_name}].primaries.fielddata.memory-size": Stat(
        "gauge",
        "primaries.fielddata.memory_size_in_bytes"),
    "indices[index={index_name}].primaries.fielddata.evictions": Stat(
        "counter",
        "primaries.fielddata.evictions"),

    # REFRESH
    "indices[index={index_name}].primaries.refresh.total-time":
        Stat("counter", "primaries.refresh.total_time_in_millis"),
    "indices[index={index_name}].primaries.refresh.total":
        Stat("counter", "primaries.refresh.total"),

    # MERGES
    "indices[index={index_name}].primaries.merges.total-docs":
        Stat("counter", "primaries.merges.total_docs"),
    "indices[index={index_name}].primaries.merges.total-size":
        Stat("bytes", "primaries.merges.total_size_in_bytes"),
    "indices[index={index_name}].primaries.merges.current":
        Stat("gauge", "primaries.merges.current"),
    "indices[index={index_name}].primaries.merges.total":
        Stat("counter", "primaries.merges.total"),
    "indices[index={index_name}].primaries.merges.current-docs":
        Stat("gauge", "primaries.merges.current_docs"),
    "indices[index={index_name}].primaries.merges.total-time":
        Stat("counter", "primaries.merges.total_time_in_millis"),
    "indices[index={index_name}].primaries.merges.current-size":
        Stat("gauge", "primaries.merges.current_size_in_bytes"),

    # COMPELTION
    "indices[index={index_name}].primaries.completion.size":
        Stat("gauge", "primaries.completion.size_in_bytes"),

    # PERCOLATE
    "indices[index={index_name}].primaries.percolate.total":
        Stat("counter", "primaries.percolate.total"),
    "indices[index={index_name}].primaries.percolate.memory-size":
        Stat("gauge", "primaries.percolate.memory_size_in_bytes"),
    "indices[index={index_name}].primaries.percolate.queries":
        Stat("counter", "primaries.percolate.queries"),
    "indices[index={index_name}].primaries.percolate.time":
        Stat("counter", "primaries.percolate.time_in_millis"),
    "indices[index={index_name}].primaries.percolate.current":
        Stat("gauge", "primaries.percolate.current"),

    # FILTER_CACHE
    "indices[index={index_name}].primaries.filter-cache.evictions":
        Stat("counter", "primaries.filter_cache.evictions"),
    "indices[index={index_name}].primaries.filter-cache.memory-size":
        Stat("gauge", "primaries.filter_cache.memory_size_in_bytes"),

    # DOCS
    "indices[index={index_name}].primaries.docs.count":
        Stat("gauge", "primaries.docs.count"),
    "indices[index={index_name}].primaries.docs.deleted":
        Stat("gauge", "primaries.docs.deleted"),

    # STORE
    "indices[index={index_name}].primaries.store.size":
        Stat("gauge", "primaries.store.size_in_bytes"),
    "indices[index={index_name}].primaries.store.throttle-time":
        Stat("counter", "primaries.store.throttle_time_in_millis"),

    # INDEXING
    "indices[index={index_name}].primaries.indexing.index-total":
        Stat("counter", "primaries.indexing.index_total"),
    "indices[index={index_name}].primaries.indexing.index-time":
        Stat("counter", "primaries.indexing.index_time_in_millis"),
    "indices[index={index_name}].primaries.indexing.index-current":
        Stat("gauge", "primaries.indexing.index_current"),
    "indices[index={index_name}].primaries.indexing.delete-total":
        Stat("counter", "primaries.indexing.delete_total"),
    "indices[index={index_name}].primaries.indexing.delete-time":
        Stat("counter", "primaries.indexing.delete_time_in_millis"),
    "indices[index={index_name}].primaries.indexing.delete-current":
        Stat("gauge", "primaries.indexing.delete_current"),

    # GET
    "indices[index={index_name}].primaries.get.time":
        Stat("counter", "primaries.get.time_in_millis"),
    "indices[index={index_name}].primaries.get.exists-total":
        Stat("counter", "primaries.get.exists_total"),
    "indices[index={index_name}].primaries.get.exists-time":
        Stat("counter", "primaries.get.exists_time_in_millis"),
    "indices[index={index_name}].primaries.get.missing-total":
        Stat("counter", "primaries.get.missing_total"),
    "indices[index={index_name}].primaries.get.missing-time":
        Stat("counter", "primaries.get.missing_time_in_millis"),
    "indices[index={index_name}].primaries.get.current":
        Stat("gauge", "primaries.get.current"),

    # SEARCH
    "indices[index={index_name}].primaries.search.open-contexts":
        Stat("gauge", "primaries.search.open_contexts"),
    "indices[index={index_name}].primaries.search.query-total":
        Stat("counter", "primaries.search.query_total"),
    "indices[index={index_name}].primaries.search.query-time":
        Stat("counter", "primaries.search.query_time_in_millis"),
    "indices[index={index_name}].primaries.search.query-current":
        Stat("gauge", "primaries.search.query_current"),
    "indices[index={index_name}].primaries.search.fetch-total":
        Stat("counter", "primaries.search.fetch_total"),
    "indices[index={index_name}].primaries.search.fetch-time":
        Stat("counter", "primaries.search.fetch_time_in_millis"),
    "indices[index={index_name}].primaries.search.fetch-current":
        Stat("gauge", "primaries.search.fetch_current"),

    # TOTAL #
    # DOCS
    "indices[index={index_name}].total.docs.count":
        Stat("gauge", "total.docs.count"),
    "indices[index={index_name}].total.docs.deleted":
        Stat("gauge", "total.docs.deleted"),

    # STORE
    "indices[index={index_name}].total.store.size":
        Stat("gauge", "total.store.size_in_bytes"),
    "indices[index={index_name}].total.store.throttle-time":
        Stat("counter", "total.store.throttle_time_in_millis"),

    # INDEXING
    "indices[index={index_name}].total.indexing.index-total":
        Stat("counter", "total.indexing.index_total"),
    "indices[index={index_name}].total.indexing.index-time":
        Stat("counter", "total.indexing.index_time_in_millis"),
    "indices[index={index_name}].total.indexing.index-current":
        Stat("gauge", "total.indexing.index_current"),
    "indices[index={index_name}].total.indexing.delete-total":
        Stat("counter", "total.indexing.delete_total"),
    "indices[index={index_name}].total.indexing.delete-time":
        Stat("counter", "total.indexing.delete_time_in_millis"),
    "indices[index={index_name}].total.indexing.delete-current":
        Stat("gauge", "total.indexing.delete_current"),

    # GET
    "indices[index={index_name}].total.get.total":
        Stat("counter", "total.get.total"),
    "indices[index={index_name}].total.get.time":
        Stat("counter", "total.get.time_in_millis"),
    "indices[index={index_name}].total.get.exists-total":
        Stat("counter", "total.get.exists_total"),
    "indices[index={index_name}].total.get.exists-time":
        Stat("counter", "total.get.exists_time_in_millis"),
    "indices[index={index_name}].total.get.missing-total":
        Stat("counter", "total.get.missing_total"),
    "indices[index={index_name}].total.get.missing-time":
        Stat("counter", "total.get.missing_time_in_millis"),
    "indices[index={index_name}].total.get.current":
        Stat("gauge", "total.get.current"),

    # SEARCH
    "indices[index={index_name}].total.search.open-contexts":
        Stat("gauge", "total.search.open_contexts"),
    "indices[index={index_name}].total.search.query-total":
        Stat("counter", "total.search.query_total"),
    "indices[index={index_name}].total.search.query-time":
        Stat("counter", "total.search.query_time_in_millis"),
    "indices[index={index_name}].total.search.query-current":
        Stat("gauge", "total.search.query_current"),
    "indices[index={index_name}].total.search.fetch-total":
        Stat("counter", "total.search.fetch_total"),

    # MERGES
    "indices[index={index_name}].total.merges.total-docs":
        Stat("counter", "total.merges.total_docs"),
    "indices[index={index_name}].total.merges.total-size":
        Stat("bytes", "total.merges.total_size_in_bytes"),
    "indices[index={index_name}].total.merges.current":
        Stat("gauge", "total.merges.current"),
    "indices[index={index_name}].total.merges.total":
        Stat("counter", "total.merges.total"),
    "indices[index={index_name}].total.merges.current-docs":
        Stat("gauge", "total.merges.current_docs"),
    "indices[index={index_name}].total.merges.total-time":
        Stat("counter", "total.merges.total_time_in_millis"),
    "indices[index={index_name}].total.merges.current-size":
        Stat("gauge", "total.merges.current_size_in_bytes"),

    # FILTER_CACHE
    "indices[index={index_name}].total.filter-cache.evictions":
        Stat("counter", "total.filter_cache.evictions"),
    "indices[index={index_name}].total.filter-cache.memory-size":
        Stat("gauge", "total.filter_cache.memory_size_in_bytes"),

    # FIELDDATA
    "indices[index={index_name}].total.fielddata.memory-size":
        Stat("gauge", "total.fielddata.memory_size_in_bytes"),
    "indices[index={index_name}].total.fielddata.evictions":
        Stat("counter", "total.fielddata.evictions"),

}

# ElasticSearch cluster stats (1.0.0 and later)
CLUSTER_STATS = {
    'cluster.active-primary-shards': Stat("gauge", "active_primary_shards"),
    'cluster.active-shards': Stat("gauge", "active_shards"),
    'cluster.initializing-shards': Stat("gauge", "initializing_shards"),
    'cluster.number-of-data_nodes': Stat("gauge", "number_of_data_nodes"),
    'cluster.number-of-nodes': Stat("gauge", "number_of_nodes"),
    'cluster.relocating-shards': Stat("gauge", "relocating_shards"),
    'cluster.unassigned-shards': Stat("gauge", "unassigned_shards"),
    'cluster.status': Stat("gauge", "status"),
}

# Thread pool metrics
THREAD_POOL_METRICS = {
    "gauge": ['threads', 'queue', 'active', 'largest'],
    "counter": ['completed', 'rejected'],
}


# collectd callbacks
def read_callback():
    """called by collectd to gather stats. It is called per collection
    interval.
    If this method throws, the plugin will be skipped for an increasing amount
    of time until it returns normally again"""
    log.info('Read callback called')
    fetch_stats()


def str_to_bool(value):
    """Python 2.x does not have a casting mechanism for booleans.  The built in
    bool() will return true for any string with a length greater than 0.  It
    does not cast a string with the text "true" or "false" to the
    corresponding bool value.  This method is a casting function.  It is
    insensetive to case and leading/trailing spaces.  An Exception is raised
    if a cast can not be made.
    """
    if str(value).strip().lower() == "true":
        return True
    elif str(value).strip().lower() == "false":
        return False
    else:
        raise Exception("Unable to cast value (%s) to boolean" % value)


def configure_callback(conf):
    """called by collectd to configure the plugin. This is called only once"""
    global ES_HOST, ES_PORT, ES_NODE_URL, ES_VERSION, \
        ES_CLUSTER, ES_INDEX, ENABLE_INDEX_STATS, ENABLE_CLUSTER_STATS, \
        DETAILED_METRICS, COLLECTION_INTERVAL, INDEX_INTERVAL, \
        CONFIGURED_THREAD_POOLS, DEFAULTS, ES_USERNAME, ES_PASSWORD, \
        MASTER_ONLY

    for node in conf.children:
        if node.key == 'Host':
            ES_HOST = node.values[0]
        elif node.key == 'Port':
            ES_PORT = int(node.values[0])
        elif node.key == 'Username':
            ES_USERNAME = node.values[0]
        elif node.key == 'Password':
            ES_PASSWORD = node.values[0]
        elif node.key == 'Verbose':
            handle.verbose = str_to_bool(node.values[0])
        elif node.key == 'Cluster':
            ES_CLUSTER = node.values[0]
            log.notice(
                'overriding elasticsearch cluster name to %s' % ES_CLUSTER)
        elif node.key == 'Version':
            ES_VERSION = node.values[0]
            log.notice(
                'overriding elasticsearch version number to %s' % ES_VERSION)
        elif node.key == 'Indexes':
            ES_INDEX = node.values
        elif node.key == 'EnableIndexStats':
            ENABLE_INDEX_STATS = str_to_bool(node.values[0])
        elif node.key == 'EnableClusterHealth':
            ENABLE_CLUSTER_STATS = str_to_bool(node.values[0])
        elif node.key == 'Interval':
            COLLECTION_INTERVAL = int(node.values[0])
        elif node.key == 'IndexInterval':
            INDEX_INTERVAL = int(node.values[0])
        elif node.key == "DetailedMetrics":
            DETAILED_METRICS = str_to_bool(node.values[0])
        elif node.key == "ThreadPools":
            for thread_pool in node.values:
                CONFIGURED_THREAD_POOLS.add(thread_pool)
            # Include required thread pools (search and index)
            CONFIGURED_THREAD_POOLS.add('search')
            CONFIGURED_THREAD_POOLS.add('index')
        elif node.key == "AdditionalMetrics":
            for metric_name in node.values:
                DEFAULTS.add(metric_name)
        elif node.key == "IndexStatsMasterOnly":
            MASTER_ONLY = str_to_bool(node.values[0])
        else:
            log.warning('Unknown config key: %s.' % node.key)

    log.info('HOST: %s' % ES_HOST)
    log.info('PORT: %s' % ES_PORT)
    log.info('ES_INDEX: %s' % ES_INDEX)
    log.info('ENABLE_INDEX_STATS: %s' % ENABLE_INDEX_STATS)
    log.info('ENABLE_CLUSTER_STATS: %s' % ENABLE_CLUSTER_STATS)
    log.info('COLLECTION_INTERVAL: %s' % COLLECTION_INTERVAL)
    log.info('INDEX_INTERVAL: %s' % INDEX_INTERVAL)
    log.info('DETAILED_METRICS: %s' % DETAILED_METRICS)
    log.info('CONFIGURED_THREAD_POOLS: %s' % CONFIGURED_THREAD_POOLS)
    log.info('METRICS TO COLLECT: %s' % DEFAULTS)
    log.info('MASTER_ONLY: %s' % MASTER_ONLY)

    # determine node information
    load_es_info()

    # intialize stats map based on ES version
    init_stats()

    # register the read callback now that we have the complete config
    collectd.register_read(read_callback, interval=COLLECTION_INTERVAL)
    log.notice(
        'started elasticsearch plugin with interval = %d seconds' %
        COLLECTION_INTERVAL)


def sanatize_intervals():
    """Sanatizes the index interval to be greater or equal to and divisible by
    the colleciton interval
    """
    global INDEX_INTERVAL, COLLECTION_INTERVAL, INDEX_SKIP, SKIP_COUNT
    # Sanitize the COLLECTION_INTERVAL and INDEX_INTERVAL
    # ? INDEX_INTERVAL > COLLECTION_INTERVAL:
    # check if INDEX_INTERVAL is divisible by COLLECTION_INTERVAL
    if INDEX_INTERVAL > COLLECTION_INTERVAL:
        # ? INDEX_INTERVAL % COLLECTION_INTERVAL > 0:
        # round the INDEX_INTERVAL up to a compatible value
        if INDEX_INTERVAL % COLLECTION_INTERVAL > 0:
            INDEX_INTERVAL = INDEX_INTERVAL + COLLECTION_INTERVAL - \
                              (INDEX_INTERVAL % COLLECTION_INTERVAL)
            log.warning('The Elasticsearch Index Interval must be \
greater or equal to than and divisible by the collection Interval.  The \
Elasticsearch Index Interval has been rounded to: %s' % INDEX_INTERVAL)

    # ? INDEX_INTERVAL < COLLECTION_INTERVAL :
    #   Set INDEX_INTERVAL = COLLECTION_INTERVAL
    elif INDEX_INTERVAL < COLLECTION_INTERVAL:
        INDEX_INTERVAL = COLLECTION_INTERVAL
        log.warning('WARN: The Elasticsearch Index Interval must be greater \
or equal to than and divisible by the collection Interval.  The Elasticsearch \
Index Interval has been rounded to: %s' % INDEX_INTERVAL)

    # INDEX_SKIP = INDEX_INTERVAL / COLLECTION_INTERVAL
    INDEX_SKIP = (INDEX_INTERVAL / COLLECTION_INTERVAL)

    # ENSURE INDEX IS COLLECTED ON THE FIRST COLLECTION
    SKIP_COUNT = INDEX_SKIP


def remove_deprecated_node_stats():
    """Remove deprecated node stats from the list of stats to collect"""
    global DEPRECATED_NODE_STATS, ES_VERSION, NODE_STATS_CUR
    NODE_STATS_CUR = remove_deprecated_elements(DEPRECATED_NODE_STATS,
                                                NODE_STATS_CUR,
                                                ES_VERSION)


def remove_deprecated_threads():
    """Remove deprecated thread_pools from the list of stats to collect"""
    global DEPRECATED_THREAD_POOLS, ES_VERSION, THREAD_POOLS
    THREAD_POOLS = remove_deprecated_elements(DEPRECATED_THREAD_POOLS,
                                              THREAD_POOLS,
                                              ES_VERSION)


def remove_deprecated_elements(deprecated, elements, version):
    """Remove deprecated items from a list or dictionary"""
    # Attempt to parse the major, minor, and revision
    (major, minor, revision) = version.split('.')

    # Sanatize alphas and betas from revision number
    revision = revision.split('-')[0]

    # Iterate over deprecation lists and remove any keys that were deprecated
    # prior to the current version
    for dep in deprecated:
        if (major >= dep['major']) \
            or (major == dep['major'] and minor >= dep['minor']) \
            or (major == dep['major'] and minor == dep['minor'] and
                revision >= dep['revision']):
            if type(elements) is list:
                for key in dep['keys']:
                    if key in elements:
                        elements.remove(key)
            if type(elements) is dict:
                for key in dep['keys']:
                    if key in elements:
                        del elements[key]
    return elements


# helper methods
def init_stats():
    global ES_HOST, ES_PORT, ES_NODE_URL, ES_CLUSTER_URL, ES_INDEX_URL, \
        ES_VERSION, NODE_STATS_CUR, INDEX_STATS_CUR, \
        CLUSTER_STATS_CUR, ENABLE_INDEX_STATS, ENABLE_CLUSTER_STATS, \
        INDEX_INTERVAL, INDEX_SKIP, COLLECTION_INTERVAL, SKIP_COUNT, \
        DEPRECATED_NODE_STATS, THREAD_POOLS, CONFIGURED_THREAD_POOLS

    sanatize_intervals()

    ES_NODE_URL = "http://" + ES_HOST + ":" + str(ES_PORT) + \
                  "/_nodes/_local/stats/transport,http,process,jvm,indices," \
                  "thread_pool"
    NODE_STATS_CUR = dict(NODE_STATS.items())
    INDEX_STATS_CUR = dict(INDEX_STATS.items())
    if not ES_VERSION.startswith("1."):
        NODE_STATS_CUR.update(NODE_STATS_ES_2)

    remove_deprecated_node_stats()

    if ES_VERSION.startswith("1.1") or ES_VERSION.startswith("1.2"):
        INDEX_STATS_CUR.update(INDEX_STATS_ES_1_1)
    else:
        # 1.3 and higher
        INDEX_STATS_CUR.update(INDEX_STATS_ES_1_1)
        INDEX_STATS_CUR.update(INDEX_STATS_ES_1_3)

    # version agnostic settings
    if not ES_INDEX:
        # get all index stats
        ES_INDEX_URL = "http://" + ES_HOST + \
                       ":" + str(ES_PORT) + "/_all/_stats"
    else:
        ES_INDEX_URL = "http://" + ES_HOST + ":" + \
                       str(ES_PORT) + "/" + ",".join(ES_INDEX) + "/_stats"

    # common thread pools for all ES versions
    thread_pools = ['generic', 'index', 'get', 'snapshot', 'bulk', 'warmer',
                    'flush', 'search', 'refresh']

    # Add the 1.0 metrics
    if not ES_VERSION.startswith("0."):
        thread_pools.extend(['merge', 'optimize'])

    # Add the 2.0 metrics
    if not ES_VERSION.startswith("1."):
        thread_pools.extend(['suggest', 'percolate', 'management', 'listener',
                             'fetch_shard_store', 'fetch_shard_started'])

    # Add the 2.1 metrics
    if not ES_VERSION.startswith("1.") and not ES_VERSION.startswith("2.0"):
        thread_pools.extend(['force_merge'])

    # Legacy support for old configurations without Thread Pools configuration
    if len(CONFIGURED_THREAD_POOLS) == 0:
        THREAD_POOLS = list(CONFIGURED_THREAD_POOLS)
    else:
        # Filter out the thread pools that aren't specified by user
        THREAD_POOLS = filter(lambda pool: pool in CONFIGURED_THREAD_POOLS,
                              thread_pools)

    remove_deprecated_threads()

    ES_CLUSTER_URL = "http://" + ES_HOST + \
                     ":" + str(ES_PORT) + "/_cluster/health"

    log.notice('Initialized with version=%s, host=%s, port=%s, url=%s' %
               (ES_VERSION, ES_HOST, ES_PORT, ES_NODE_URL))


# FUNCTION: Collect node stats from JSON result
def lookup_node_stat(stat, json):
    node = json['nodes'].keys()[0]
    val = dig_it_up(json, NODE_STATS_CUR[stat].path % node)

    # Check to make sure we have a valid result
    # dig_it_up returns False if no match found
    if not isinstance(val, bool):
        return int(val)
    else:
        return None


def fetch_stats():
    """
    fetches all required stats from ElasticSearch. This method also sets
    ES_CLUSTER
    """
    global ES_CLUSTER, SKIP_COUNT, INDEX_SKIP, THREAD_POOLS

    node_json_stats = fetch_url(ES_NODE_URL)
    if node_json_stats:
        if ES_CLUSTER is None:
            ES_CLUSTER = node_json_stats['cluster_name']
        else:
            log.info('Configured with cluster_json_stats=%s' % ES_CLUSTER)
        log.info('Parsing node_json_stats')
        parse_node_stats(node_json_stats, NODE_STATS_CUR)
        log.info('Parsing thread pool stats')
        parse_thread_pool_stats(node_json_stats, THREAD_POOLS)

    # check the current master
    detect_es_master()

    # load cluster and index stats only on master eligible nodes, this
    # avoids collecting too many metrics if the cluster has a lot of nodes
    if ENABLE_CLUSTER_STATS and ES_MASTER_ELIGIBLE:
        cluster_json_stats = fetch_url(ES_CLUSTER_URL)
        log.info('Parsing cluster stats')
        parse_cluster_stats(cluster_json_stats, CLUSTER_STATS)

    if (ENABLE_INDEX_STATS and ES_MASTER_ELIGIBLE and
        SKIP_COUNT >= INDEX_SKIP) \
        and ((MASTER_ONLY and ES_CURRENT_MASTER)
             or (not MASTER_ONLY)):
        # Reset skip count
        SKIP_COUNT = 0
        indices = fetch_url(ES_INDEX_URL)
        if indices:
            indexes_json_stats = indices['indices']
            for index_name in indexes_json_stats.keys():
                log.info('Parsing index stats for index: %s' % index_name)
                parse_index_stats(indexes_json_stats[index_name], index_name)
    # Incrememnt skip count
    SKIP_COUNT += 1


def fetch_url(url):
    response = None
    try:
        log.info('Fetching api information from: %s' % url)
        request = urllib2.Request(url)
        if ES_USERNAME:
            authheader = base64.encodestring('%s:%s' %
                                             (ES_USERNAME, ES_PASSWORD)
                                             ).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % authheader)
        response = urllib2.urlopen(request, timeout=10)
        log.info('Raw api response: %s' % response)
        return json.load(response)
    except (urllib2.URLError, urllib2.HTTPError), e:
        log.error('Error connecting to %s - %r : %s' %
                  (url, e, e))
        return None
    finally:
        if response is not None:
            response.close()


def load_es_info():
    global ES_VERSION, ES_CLUSTER, ES_MASTER_ELIGIBLE, NODE_ID

    json = fetch_url("http://" + ES_HOST + ":" + str(ES_PORT) +
                     "/_nodes/_local")
    if json is None:
        # assume some sane defaults
        if ES_VERSION is None:
            ES_VERSION = "1.0.0"
        if ES_CLUSTER is None:
            ES_CLUSTER = "elasticsearch"
        ES_MASTER_ELIGIBLE = True
        log.warning('Unable to determine node \
information, defaulting to version %s, cluster %s and master %s' %
                    (ES_VERSION, ES_CLUSTER, ES_MASTER_ELIGIBLE))
        return

    # Identify the current node
    NODE_ID = json['nodes'].keys()[0]
    log.notice('current node id: %s' % NODE_ID)

    cluster_name = json['cluster_name']
    # we should have only one entry with the current node information
    node_info = json['nodes'].itervalues().next()
    version = node_info['version']
    # a node is master eligible by default unless it's configured otherwise
    master_eligible = True
    if 'node' in node_info['settings'] and \
       'master' in node_info['settings']['node']:
        master_eligible = node_info['settings']['node']['master'] == 'true'

    # update global settings
    ES_MASTER_ELIGIBLE = master_eligible
    if ES_VERSION is None:
        ES_VERSION = version
    if ES_CLUSTER is None:
        ES_CLUSTER = cluster_name

    log.notice('version: %s, cluster: %s, master eligible: %s' %
               (ES_VERSION, ES_CLUSTER, ES_MASTER_ELIGIBLE))


def detect_es_master():
    """Determines if this is the current master. This method sets
    ES_CURRENT_MASTER"""
    global ES_CURRENT_MASTER
    # determine current master
    cluster_state = fetch_url("http://" + ES_HOST + ":" + str(ES_PORT) +
                              "/_cluster/state/master_node")
    if ES_CURRENT_MASTER is False and cluster_state['master_node'] == NODE_ID:
        ES_CURRENT_MASTER = True
        log.notice('current master: %s' % ES_CURRENT_MASTER)
    elif ES_CURRENT_MASTER is True and cluster_state['master_node'] != NODE_ID:
        ES_CURRENT_MASTER = False
        log.notice('current master: %s' % ES_CURRENT_MASTER)
    else:
        log.debug('current master: %s' % ES_CURRENT_MASTER)


def parse_node_stats(json, stats):
    """Parse node stats response from ElasticSearch"""
    for name, key in stats.iteritems():
        if DETAILED_METRICS is True or name in DEFAULTS:
            result = lookup_node_stat(name, json)
            dispatch_stat(result, name, key)


def parse_thread_pool_stats(json, stats):
    """Parse thread pool stats response from ElasticSearch"""
    for pool in THREAD_POOLS:
        for metric_type, value in THREAD_POOL_METRICS.iteritems():
            for attr in value:
                name = 'thread_pool.{0}'.format(attr)
                key = Stat(metric_type, 'nodes.%s.thread_pool.{0}.{1}'.
                           format(pool, attr))
                if DETAILED_METRICS is True or name in DEFAULTS:
                    node = json['nodes'].keys()[0]
                    result = dig_it_up(json, key.path % node)
                    # Check to make sure we have a valid result
                    # dig_it_up returns False if no match found
                    if not isinstance(result, bool):
                        result = int(result)
                    else:
                        result = None

                    dispatch_stat(result, name, key, {'thread_pool': pool})


def parse_cluster_stats(json, stats):
    """Parse cluster stats response from ElasticSearch"""
    # convert the status color into a number
    json['status'] = CLUSTER_STATUS[json['status']]
    for name, key in stats.iteritems():
        if DETAILED_METRICS is True or name in DEFAULTS:
            result = dig_it_up(json, key.path)
            dispatch_stat(result, name, key)


def parse_index_stats(json, index_name):
    """Parse index stats response from ElasticSearch"""
    for name, key in INDEX_STATS_CUR.iteritems():
        # filter default metrics
        if DETAILED_METRICS is True or \
           name.replace("[index={index_name}]", "") in DEFAULTS:
            result = dig_it_up(json, key.path)
            # update the index name in the type_instance to include
            # the index as a dimensions
            name = name.format(index_name=sanitize_type_instance(index_name))
            dispatch_stat(result, name, key)


def sanitize_type_instance(index_name):
    """
    collectd limit the character set in type_instance to ascii and forbids
    the '/' character. This method does a lossy conversion to ascii and
    replaces the reserved character with '_'
    """
    ascii_index_name = index_name.encode('ascii', 'ignore')
    # '/' is reserved, so we substitute it with '_' instead
    return ascii_index_name.replace('/', '_')


def dispatch_stat(result, name, key, dimensions=None):
    """Read a key from info response data and dispatch a value"""
    log.info(('Parameters to be emitted:\n name: {n}\n key: {k}'
              '\n dimensions: {d}\n result: {r}').format(n=name,
                                                         k=key,
                                                         d=dimensions,
                                                         r=result))
    if result is None:
        log.warning('Value not found for %s' % name)
        return
    estype = key.type
    value = int(result)
    log.info('Sending value[%s]: %s=%s' % (estype, name, value))

    val = collectd.Values(plugin='elasticsearch')
    val.plugin_instance = ES_CLUSTER

    # If dimensions are provided, format them and append
    # them to the plugin_instance
    if dimensions:
        val.plugin_instance += '[{dims}]'.format(dims=','.join(['='.join(d)
                                                 for d in dimensions.items()]))

    val.type = estype
    val.type_instance = name
    val.values = [value]
    val.meta = {'0': True}
    log.info('Emitting value: %s' % val)
    val.dispatch()


def dig_it_up(obj, path):
    try:
        if type(path) in (str, unicode):
            path = path.split('.')
        return reduce(lambda x, y: x[y], path, obj)
    except:
        return False


# The following classes are there to launch the plugin manually
# with something like ./elasticsearch_collectd.py for development
# purposes. They basically mock the calls on the "collectd" symbol
# so everything prints to stdout.
class CollectdMock(object):
    def __init__(self):
        self.value_mock = CollectdValuesMock

    def debug(self, msg):
        print 'DEBUG: {0}'.format(msg)

    def info(self, msg):
        print 'INFO: {0}'.format(msg)

    def notice(self, msg):
        print 'NOTICE: {0}'.format(msg)

    def warning(self, msg):
        print 'WARN: {0}'.format(msg)

    def error(self, msg):
        print 'ERROR: {0}'.format(msg)
        sys.exit(1)

    def Values(self, plugin='elasticsearch'):
        return (self.value_mock)()


class CollectdValuesMock(object):
    def dispatch(self):
        print self

    def __str__(self):
        attrs = []
        for name in dir(self):
            if not name.startswith('_') and name is not 'dispatch':
                attrs.append("{0}={1}".format(name, getattr(self, name)))
        return "<CollectdValues {0}>".format(' '.join(attrs))


class CollectdLogHandler(logging.Handler):
    """Log handler to forward statements to collectd
    A custom log handler that forwards log messages raised
    at level debug, info, notice, warning, and error
    to collectd's built in logging.  Suppresses extraneous
    info and debug statements using a "verbose" boolean

    Inherits from logging.Handler

    Arguments
        plugin -- name of the plugin (default 'unknown')
        verbose -- enable/disable verbose messages (default False)
    """
    def __init__(self, plugin="elasticsearch", verbose=False):
        """Initializes CollectdLogHandler
        Arguments
            plugin -- string name of the plugin (default 'unknown')
            verbose -- enable/disable verbose messages (default False)
        """
        self.verbose = verbose
        self.plugin = plugin
        logging.Handler.__init__(self, level=logging.NOTSET)

    def emit(self, record):
        """
        Emits a log record to the appropraite collectd log function

        Arguments
        record -- str log record to be emitted
        """
        try:
            if record.msg is not None:
                if record.levelname == 'ERROR':
                    collectd.error('%s : %s' % (self.plugin, record.msg))
                elif record.levelname == 'WARNING':
                    collectd.warning('%s : %s' % (self.plugin, record.msg))
                elif record.levelname == 'NOTICE':
                    collectd.notice('%s : %s' % (self.plugin, record.msg))
                elif record.levelname == 'INFO' and self.verbose is True:
                    collectd.info('%s : %s' % (self.plugin, record.msg))
                elif record.levelname == 'DEBUG' and self.verbose is True:
                    collectd.debug('%s : %s' % (self.plugin, record.msg))
        except Exception as e:
            collectd.warning(('{p} [ERROR]: Failed to write log statement due '
                              'to: {e}').format(p=self.plugin,
                                                e=e
                                                ))


class CollectdLogger(logging.Logger):
    """Logs all collectd log levels via python's logging library
    Custom python logger that forwards log statements at
    level: debug, info, notice, warning, error

    Inherits from logging.Logger

    Arguments
    name -- name of the logger
    level -- log level to filter by
    """
    def __init__(self, name, level=logging.NOTSET):
        """Initializes CollectdLogger

        Arguments
        name -- name of the logger
        level -- log level to filter by
        """
        logging.Logger.__init__(self, name, level)
        logging.addLevelName(25, 'NOTICE')

    def notice(self, msg):
        """Logs a 'NOTICE' level statement at level 25

        Arguments
        msg - log statement to be logged as 'NOTICE'
        """
        self.log(25, msg)


# Set up logging
logging.setLoggerClass(CollectdLogger)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.propagate = False
handle = CollectdLogHandler(PREFIX)
log.addHandler(handle)


def configure_test():
    """Configure the plugin for testing"""
    global CONFIGURED_THREAD_POOLS, DETAILED_METRICS, INDEX_INTERVAL, \
        ENABLE_INDEX_STATS, ENABLE_CLUSTER_STATS, ES_MASTER_ELIGIBLE

    # Ensure all possible threadpools are elligible for collection
    CONFIGURED_THREAD_POOLS = set(['generic', 'index', 'get', 'snapshot',
                                   'bulk', 'warmer', 'flush', 'search',
                                   'refresh', 'suggest', 'percolate',
                                   'management', 'listener',
                                   'fetch_shard_store', 'fetch_shard_started',
                                   'force_merge', 'merge', 'optimize', ])
    DETAILED_METRICS = True
    INDEX_INTERVAL = 10
    ENABLE_INDEX_STATS = True
    ENABLE_CLUSTER_STATS = True
    ES_MASTER_ELIGIBLE = True


if __name__ == '__main__':
    import sys
    # allow user to override ES host name for easier testing
    if len(sys.argv) > 1:
        ES_HOST = sys.argv[1]
    handle.verbose = True
    collectd = CollectdMock()
    configure_test()
    load_es_info()
    init_stats()
    fetch_stats()
else:
    import collectd
    collectd.register_config(configure_callback)
