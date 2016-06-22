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

PREFIX = "elasticsearch"
ES_HOST = "localhost"
ES_PORT = 9200
ES_CLUSTER = None
ES_VERSION = None
ES_MASTER_ELIGIBLE = None

ENABLE_INDEX_STATS = True
ENABLE_CLUSTER_STATS = True

ES_NODE_URL = ""
ES_CLUSTER_URL = ""
ES_INDEX_URL = ""
ES_INDEX = []

VERBOSE_LOGGING = False

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


DEFAULTS = {
    # PAGE: Elasticsearch

    # DASHBOARD: Elasticsearch Node

    # CHART: Requests/sec
    "indices.search.query-total",
    "indices.indexing.index-total",
    "indices.get.total",

    # CHART: Document Growth Rate %
    "indices.docs.count",
    "indices.docs.count",
    "indices.docs.count",
    "indices.docs.count",

    # CHART: Indexing Requests/sec
    "indices.indexing.index-total",

    # CHART: Average Query Latency (ms)
    "indices.search.query-total",
    "indices.search.query-time",

    # CHART: File Descriptors and Segments
    "process.open_file_descriptors",
    "indices.segments.count",

    # CHART: Memory Heap Size (bytes)
    "jvm.mem.heap-used",
    "jvm.mem.heap-committed",

    # CHART: Active Merges
    "indices.merges.current",

    # CHART: Search Requests/sec
    "indices.search.query-total",

    # CHART: Merges/sec
    "indices.merges.total",

    # CHART: Thread Pool Rejections
    "thread_pool.bulk.rejected",
    "thread_pool.flush.rejected",
    "thread_pool.generic.rejected",
    "thread_pool.get.rejected",
    "thread_pool.index.rejected",
    "thread_pool.merge.rejected",
    "thread_pool.optimize.rejected",
    "thread_pool.refresh.rejected",
    "thread_pool.search.rejected",
    "thread_pool.snapshot.rejected",

    # CHART: Cache Sizes (bytes)
    "indices.cache.filter.size",
    "indices.cache.field.size",

    # CHART: GC Time %
    "jvm.gc.time",
    "jvm.uptime",

    # DASHBOARD: Elasticsearch

    # CHART: Top Clusters by Query Latency (ms)
    "indices.search.query-total",
    "indices.search.query-time",
    "indices.search.query-total",
    "indices.search.query-time",

    # CHART: Top Clusters by Indexing Requests
    "indices.indexing.index-total",

    # CHART: Merges/sec
    "indices.merges.total",

    # CHART: # Hosts/Clusters
    "indices.indexing.index-total",
    "indices.indexing.index-total",

    # CHART: Thread Pool Rejections
    "thread_pool.bulk.rejected",
    "thread_pool.flush.rejected",
    "thread_pool.generic.rejected",
    "thread_pool.get.rejected",
    "thread_pool.index.rejected",
    "thread_pool.merge.rejected",
    "thread_pool.optimize.rejected",
    "thread_pool.refresh.rejected",
    "thread_pool.search.rejected",
    "thread_pool.snapshot.rejected",

    # CHART: Search Requests
    "indices.search.query-total",

    # CHART: GC Time %
    "jvm.gc.time",
    "jvm.uptime",
    "jvm.gc.time",
    "jvm.uptime",

    # CHART: Deleted Documents %
    "indices.docs.deleted",
    "indices.docs.count",

    # CHART: Document Growth %
    "indices.docs.count",
    "indices.docs.count",

    # CHART: Cache Size (bytes)
    "indices.cache.filter.size",
    "indices.cache.field.size",

    # CHART: Top Clusters by Index Growth %
    "indices.store.size",
    "indices.store.size",

    # CHART: Top Clusters by Search Requests
    "indices.search.query-total",

    # CHART: Indexing Requests
    "indices.indexing.index-total",

    # CHART: Heap %
    "jvm.mem.heap-used",
    "jvm.mem.heap-committed",

    # DASHBOARD: Elasticsearch Cluster

    # CHART: Thread Pool Rejections
    "thread_pool.bulk.rejected",
    "thread_pool.flush.rejected",
    "thread_pool.generic.rejected",
    "thread_pool.get.rejected",
    "thread_pool.index.rejected",
    "thread_pool.merge.rejected",
    "thread_pool.optimize.rejected",
    "thread_pool.refresh.rejected",
    "thread_pool.search.rejected",
    "thread_pool.snapshot.rejected",

    # CHART: Deleted Documents %
    "indices.total.docs.deleted",
    "indices.total.docs.count",

    # CHART: GC Time %
    "jvm.gc.time",
    "jvm.uptime",
    "jvm.gc.time",
    "jvm.uptime",

    # CHART: # Nodes
    "cluster.number-of-nodes",
    "cluster.number-of-data_nodes",

    # CHART: Cache Size (bytes)
    "indices.total.filter-cache.memory-size",
    "indices.total.fielddata.memory-size",

    # CHART: Heap %
    "jvm.mem.heap-used",
    "jvm.mem.heap-committed",

    # CHART: Cluster Shard Allocation
    "cluster.unassigned-shards",
    "cluster.relocating-shards",
    "cluster.active-primary-shards",
    "cluster.active-shards",

    # PAGE: Elasticsearch Index

    # DASHBOARD: Elasticsearch Indexes

    # CHART: Top Indexes by Indexing Requests
    "indices.total.indexing.index-total",

    # CHART: Merges/sec
    "indices.total.merges.total",

    # CHART: Top Indexes by Search Requests
    "indices.total.search.query-total",

    # CHART: Search Requests/sec
    "indices.total.search.query-total",

    # CHART: Indexing Requests/sec
    "indices.total.indexing.index-total",

    # CHART: Top Indexes by Index Size Growth %
    "indices.total.store.size",
    "indices.total.store.size",

    # CHART: Top Indexes by Query Latency (ms)
    "indices.total.search.query-total",
    "indices.total.search.query-time",

    # CHART: Document Growth %
    "indices.total.docs.count",

    # DASHBOARD: Elasticsearch Index

    # CHART: Deleted Documents %
    "indices.total.docs.deleted",
    "indices.total.docs.count",

    # CHART: Cache Size (bytes)
    "indices.total.filter-cache.memory-size",
    "indices.total.fielddata.memory-size",

    # CHART: Merge Latency (ms)
    "indices.total.merges.total",
    "indices.total.merges.total-time",

    # CHART: Search Requests/sec
    "indices.total.search.query-total",

    # CHART: Elasticsearch Tips

    # CHART: Index Statistics
    "indices.total.store.size",
    "indices.total.store.size",
    "indices.total.docs.count",

    # CHART: Search Latency (ms)
    "indices.total.search.query-total",
    "indices.total.search.query-time",

    # CHART: Index Latency (ms)
    "indices.total.indexing.index-total",
    "indices.total.indexing.index-time",

    # CHART: Merges/sec
    "indices.total.merges.total",

    # CHART: Indexing Requests/sec
    "indices.total.indexing.index-total",

    # CHART: Document Growth %
    "indices.total.docs.count",

    # ADD ADDITIONAL METRIC NAMES
    # TO INCLUDE BY DEFAULT
}

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
    log_verbose('Read callback called')
    fetch_stats()


def _bool(value):
    """Python 2.x does not have a casting mechanism for booleans.  The built in
    bool() will return true for any string with a length greater than 0.  It
    does not cast a string with the text "true" or "false" to the
    corresponding bool value.  This method is a casting function.  It is
    insensetive to case and leading/trailing spaces.  An Exception is raised
    if a cast can not be made.
    """
    if str(value).strip().lower() in "true":
        return True
    elif str(value).strip().lower() in "false":
        return False
    else:
        raise Exception("Unable to cast value (%s) to boolean" % value)


def configure_callback(conf):
    """called by collectd to configure the plugin. This is called only once"""
    global ES_HOST, ES_PORT, ES_NODE_URL, ES_VERSION, VERBOSE_LOGGING, \
        ES_CLUSTER, ES_INDEX, ENABLE_INDEX_STATS, ENABLE_CLUSTER_STATS, \
        DETAILED_METRICS, COLLECTION_INTERVAL, INDEX_INTERVAL, \
        CONFIGURED_THREAD_POOLS, DEFAULTS

    for node in conf.children:
        if node.key == 'Host':
            ES_HOST = node.values[0]
        elif node.key == 'Port':
            ES_PORT = int(node.values[0])
        elif node.key == 'Verbose':
            VERBOSE_LOGGING = _bool(node.values[0])
        elif node.key == 'Cluster':
            ES_CLUSTER = node.values[0]
            collectd.info(
                "overriding elasticsearch cluster name to %s" % ES_CLUSTER)
        elif node.key == 'Version':
            ES_VERSION = node.values[0]
            collectd.info(
                "overriding elasticsearch version number to %s" % ES_VERSION)
        elif node.key == 'Indexes':
            ES_INDEX = node.values
        elif node.key == 'EnableIndexStats':
            ENABLE_INDEX_STATS = _bool(node.values[0])
        elif node.key == 'EnableClusterHealth':
            ENABLE_CLUSTER_STATS = _bool(node.values[0])
        elif node.key == 'Interval':
            COLLECTION_INTERVAL = int(node.values[0])
        elif node.key == 'IndexInterval':
            INDEX_INTERVAL = int(node.values[0])
        elif node.key == "DetailedMetrics":
            DETAILED_METRICS = _bool(node.values[0])
        elif node.key == "ThreadPools":
            for i in node.values:
                CONFIGURED_THREAD_POOLS.add(i)
            # Include required thread pools (search and index)
            CONFIGURED_THREAD_POOLS.add('search')
            CONFIGURED_THREAD_POOLS.add('index')
            log_verbose('CONFIGURED_THREAD_POOLS: %s' %
                        CONFIGURED_THREAD_POOLS)
        elif node.key == "AdditionalDefaultMetrics":
            for i in node.values:
                DEFAULTS.add(i)
                log_verbose('Adding %s to the list of default metrics' % i)
        else:
            collectd.warning('elasticsearch plugin: Unknown config key: %s.'
                             % node.key)

    # determine node information
    load_es_info()

    # intialize stats map based on ES version
    init_stats()

    # register the read callback now that we have the complete config
    collectd.register_read(read_callback, interval=COLLECTION_INTERVAL)
    collectd.info(
        "started elasticsearch plugin with interval = %d seconds" %
        COLLECTION_INTERVAL)


# helper methods
def init_stats():
    global ES_HOST, ES_PORT, ES_NODE_URL, ES_CLUSTER_URL, ES_INDEX_URL, \
        ES_VERSION, VERBOSE_LOGGING, NODE_STATS_CUR, INDEX_STATS_CUR, \
        CLUSTER_STATS_CUR, ENABLE_INDEX_STATS, ENABLE_CLUSTER_STATS, \
        INDEX_INTERVAL, INDEX_SKIP, COLLECTION_INTERVAL, SKIP_COUNT, \
        DEPRECATED_NODE_STATS, THREAD_POOLS, CONFIGURED_THREAD_POOLS

    # Sanitize the COLLECTION_INTERVAL and INDEX_INTERVAL
    # ? INDEX_INTERVAL > COLLECTION_INTERVAL:
    # check if INDEX_INTERVAL is divisible by COLLECTION_INTERVAL
    if INDEX_INTERVAL > COLLECTION_INTERVAL:
        # ? INDEX_INTERVAL % COLLECTION_INTERVAL > 0:
        # round the INDEX_INTERVAL up to a compatible value
        if INDEX_INTERVAL % COLLECTION_INTERVAL > 0:
            INDEX_INTERVAL = INDEX_INTERVAL + COLLECTION_INTERVAL - \
                              (INDEX_INTERVAL % COLLECTION_INTERVAL)
            collectd.info("WARN: The Elasticsearch Index Interval must be \
greater or equal to than and divisible by the collection Interval.  The \
Elasticsearch Index Interval has been rounded to: %s" % INDEX_INTERVAL)

    # ? INDEX_INTERVAL < COLLECTION_INTERVAL :
    #   Set INDEX_INTERVAL = COLLECTION_INTERVAL
    elif INDEX_INTERVAL < COLLECTION_INTERVAL:
        INDEX_INTERVAL = COLLECTION_INTERVAL
        collectd.info("WARN: The Elasticsearch Index Interval must be greater \
or equal to than and divisible by the collection Interval.  The Elasticsearch \
Index Interval has been rounded to: %s" % INDEX_INTERVAL)

    # INDEX_SKIP = INDEX_INTERVAL / COLLECTION_INTERVAL
    INDEX_SKIP = (INDEX_INTERVAL / COLLECTION_INTERVAL)

    # ENSURE INDEX IS COLLECTED ON THE FIRST COLLECTION
    SKIP_COUNT = INDEX_SKIP

    ES_NODE_URL = "http://" + ES_HOST + ":" + str(ES_PORT) + \
                  "/_nodes/_local/stats/transport,http,process,jvm,indices," \
                  "thread_pool"
    NODE_STATS_CUR = dict(NODE_STATS.items())
    INDEX_STATS_CUR = dict(INDEX_STATS.items())
    if ES_VERSION.startswith("2."):
        NODE_STATS_CUR.update(NODE_STATS_ES_2)

    # Attempt to parse the major, minor, and revision
    major = ES_VERSION.split('.')[0]
    minor = ES_VERSION.split('.')[1]
    revision = ES_VERSION.split('.')[2]

    # Iterate over deprecation lists and remove any keys that were deprecated
    # prior to the current version
    for dep in DEPRECATED_NODE_STATS:
        if (major >= dep['major']) \
            or (major == dep['major'] and minor >= dep['minor']) \
            or (major == dep['major'] and minor == dep['minor'] and
                revision >= dep['revision']):
            for key in dep['keys']:
                del NODE_STATS_CUR[key]

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

    if ES_VERSION.startswith("2."):
        thread_pools.extend(['suggest', 'percolate', 'management', 'listener',
                             'fetch_shard_store', 'fetch_shard_started'])
    elif ES_VERSION.startswith("2.") and not ES_VERSION.startswith("2.0"):
        thread_pools.extend(['force_merge'])
    else:
        thread_pools.extend(['merge', 'optimize'])

    # Legacy support for old configurations without Thread Pools configuration
    if len(CONFIGURED_THREAD_POOLS) <= 0:
        THREAD_POOLS = CONFIGURED_THREAD_POOLS
    else:
        # Filter out the thread pools that aren't specified by user
        THREAD_POOLS = filter(lambda pool: pool in CONFIGURED_THREAD_POOLS,
                              thread_pools)

    ES_CLUSTER_URL = "http://" + ES_HOST + \
                     ":" + str(ES_PORT) + "/_cluster/health"

    log_verbose('Configured with version=%s, host=%s, port=%s, url=%s' %
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
        ES_CLUSTER = node_json_stats['cluster_name']
        log_verbose('Configured with cluster_json_stats=%s' % ES_CLUSTER)
        log_verbose('Parsing node_json_stats')
        parse_node_stats(node_json_stats, NODE_STATS_CUR)
        log_verbose('Parsing thread pool stats')
        parse_thread_pool_stats(node_json_stats, THREAD_POOLS)

    # load cluster and index stats only on master eligible nodes, this
    # avoids collecting too many metrics if the cluster has a lot of nodes
    if ENABLE_CLUSTER_STATS and ES_MASTER_ELIGIBLE:
        cluster_json_stats = fetch_url(ES_CLUSTER_URL)
        parse_cluster_stats(cluster_json_stats, CLUSTER_STATS)

    if ENABLE_INDEX_STATS and ES_MASTER_ELIGIBLE and SKIP_COUNT >= INDEX_SKIP:
        # Reset skip count
        SKIP_COUNT = 0
        indices = fetch_url(ES_INDEX_URL)
        if indices:
            indexes_json_stats = indices['indices']
            for index_name in indexes_json_stats.keys():
                parse_index_stats(indexes_json_stats[index_name], index_name)
    # Incrememnt skip count
    SKIP_COUNT += 1


def fetch_url(url):
    response = None
    try:
        response = urllib2.urlopen(url, timeout=10)
        return json.load(response)
    except urllib2.URLError, e:
        collectd.error(
            'elasticsearch plugin: Error connecting to %s - %r' % (url, e))
        return None
    finally:
        if response is not None:
            response.close()


def load_es_info():
    global ES_VERSION, ES_CLUSTER, ES_MASTER_ELIGIBLE

    json = fetch_url("http://" + ES_HOST + ":" + str(ES_PORT) +
                     "/_nodes/_local")
    if json is None:
        # assume some sane defaults
        ES_VERSION = "1.0.0"
        ES_CLUSTER = "elasticsearch"
        ES_MASTER_ELIGIBLE = True
        collectd.warning("elasticsearch plugin: unable to determine node \
information, defaulting to version %s, cluster %s and master %s" %
                         (ES_VERSION, ES_CLUSTER, ES_MASTER_ELIGIBLE))
        return

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

    collectd.info("elasticsearch plugin: version: %s, cluster: %s, master \
eligible: %s"
                  % (ES_VERSION, ES_CLUSTER, ES_MASTER_ELIGIBLE))


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
    if result is None:
        collectd.warning('elasticsearch plugin: Value not found for %s' % name)
        return
    estype = key.type
    value = int(result)
    log_verbose('Sending value[%s]: %s=%s' % (estype, name, value))

    val = collectd.Values(plugin='elasticsearch')
    val.plugin_instance = ES_CLUSTER

    if dimensions:
        val.plugin_instance += '[{dims}]'.format(dims=','.join(['='.join(d)
                                                 for d in dimensions.items()]))

    val.type = estype
    val.type_instance = name
    val.values = [value]
    val.meta = {'0': True}
    val.dispatch()


def dig_it_up(obj, path):
    try:
        if type(path) in (str, unicode):
            path = path.split('.')
        return reduce(lambda x, y: x[y], path, obj)
    except:
        return False


def log_verbose(msg):
    if not VERBOSE_LOGGING:
        return
    collectd.info('elasticsearch plugin [verbose]: %s' % msg)


# The following classes are there to launch the plugin manually
# with something like ./elasticsearch_collectd.py for development
# purposes. They basically mock the calls on the "collectd" symbol
# so everything prints to stdout.
class CollectdMock(object):
    def __init__(self):
        self.value_mock = CollectdValuesMock

    def info(self, msg):
        print 'INFO: {}'.format(msg)

    def warning(self, msg):
        print 'WARN: {}'.format(msg)

    def error(self, msg):
        print 'ERROR: {}'.format(msg)
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
                attrs.append("{}={}".format(name, getattr(self, name)))
        return "<CollectdValues {}>".format(' '.join(attrs))


if __name__ == '__main__':
    import sys
    # allow user to override ES host name for easier testing
    if len(sys.argv) > 1:
        ES_HOST = sys.argv[1]
    collectd = CollectdMock()
    load_es_info()
    init_stats()
    fetch_stats()
else:
    import collectd
    collectd.register_config(configure_callback)
