# Elasticsearch CollectD plugin

A [CollectD](http://collectd.org) plugin to collect [Elasticsearch](https://github.com/elastic/elasticsearch) stats and metrics. Uses CollectD's [Python plugin](http://collectd.org/documentation/manpages/collectd-python.5.shtml).

## Installation

 1. Place the `elasticsearch_collectd.py` and `elasticsearch_collectd_utils.py` files into a directory on the host. The recommended directory is `/usr/share/collectd/collectd-elasticsearch`.
 1. Configure the plugin (see below).
 1. Restart collectd.

### Requirements

 * collectd 4.9+
 * Elasticsearch 1.x or newer.
 * python v2.6 or newer (https support requires v2.7.9)

## Configuration

 * See [`elasticsearch.conf`](https://github.com/signalfx/integrations/blob/master/collectd-elasticsearch/20-elasticsearch.conf)
 * The plugin will automatically determine the version of Elasticsearch you are running as well as the cluster name.
 * Per-index and cluster stats can be disabled if needed; they are enabled by default. These settings are collected only on master eligible nodes.
 * If you are running the Elasticsearch plugin via a collectd deployment within a container, please configure the Host and Port values inside of the 20-elasticsearch.conf file that correspond to the desired Elasticsearch instance.

 ex:
```
   <Module "elasticsearch_collectd">
       Host "XXX.XXX.XXX.XXX"
       Port "XXXX"
   </Module>
```

## Metrics

### Node stats

 * Documents (total docs & deleted docs)
 * Store size
 * Indexing (total, time, total delete, delete time)
 * Get (total, time, exists total, exists time, missing total, missing time)
 * Search (total query, total time, total fetch, total fetch time)
 * JVM uptime
 * JVM memory (heap committed, heap Used, non heap committed, non heap used)
 * JVM threads (count & peak)
 * JVM GC (time & count)
 * Transport stats (server open, RX count, RX size, TX count, TX size)
 * HTTP stats (current open & total open)
 * OS stats (CPU percent, file descriptors)
 * Thread pool stats (generic, index, get, snapshot, merge, optimize, bulk, warmer, flush, search, refresh)
 * Cache (field eviction, field size, filter evictions, filter size)
 * JVM collectors
 * FLush (total count, total time)
 * Merges (current count, current docs, current size, merge total size, docs a time)
 * Refresh (Total & Time)

### Index stats

 * Transaction log (size, number of operations)
 * Most of the common stats per index and per primary vs. total.

### Cluster stats

 * Shard stats (active, initializing, relocating, unassigned, primaries)
 * Nodes (total, data nodes)
