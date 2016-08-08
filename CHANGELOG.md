### CHANGELOG

This file documents important changes to the Elasticsearch plugin for collectd. 

- [2016-08-08: Restore compatibility with 
python v2.6](#2016-08-08)
- [2016-07-21: Dimensionalize thread pool metrics
by thread pool](#2016-07-21-dimensionalize-thread-pool-metrics-by-thread-pool)
- [2016-06-28: Basic configuration
changes](#2016-06-28-changes-to-basic-plugin-configuration) 
- [2016-06-27: Support for basic 
authentication](#2016-06-27-support-for-basic-authentication)

#### <a id="2016-08-08"></a> 2016-08-08: Restore compatibility with python v2.6 

This latest revision restores compatibility with Python v2.6.

#### 2016-07-21: Dimensionalize thread pool metrics by thread pool

Prior to this update, the plugin transmitted thread pool metrics with the names
of thread pools included as part of the metric name.

Ex. (Where thread_pool is "search")
```
counter.thread_pool.search.rejected
```

This update removes the name of the thread pool from the metric name and 
instead attaches the name of the thread pool in a dimension named "thread_pool". 

Ex. (Where thread_pool is "search")
```Bash
counter.thread_pool.rejected
# The metric above now has the dimension 
# named "thread_pool" set to "search"
```

SignalFx's built-in dashboards have been updated to accommodate metrics from
both before and after this change. 

When you upgrade to this version, any custom SignalFx charts and detectors that
you have built that include thread pool metrics will need to be modified to
include the new metric names. Modify charts as follows: 

1. Whenever a chart uses a metric like `counter.thread_pool.search.rejected`,
add a new plot to the chart that uses the metric `counter.thread_pool.rejected`.
1. On the new plot, apply a filter by the dimension `thread_pool`, with value
`search`, to match the previous metric. 
1. If your chart uses a timeseries expression that refers to the previous
metric, clone the expression, then modify any letter references in the clone to
refer to the new plot instead of the old one. 

For detectors, follow the procedure above, then select the new plot or new
timeseries expression as the signal. 

#### 2016-06-28: Changes to basic plugin configuration

##### Control level of metrics detail

Before this update, the plugin transmitted every metric available from
Elasticsearch's stats API. Available metrics are now segmented into two sets:
"default", a curated set of metrics used in SignalFx's built-in dashboards for
this plugin, and "detailed" which includes all available metrics. Control the
set of metrics that will be transmitted in the `DetailedMetrics` configuration
parameter. To capture additional metrics beyond those in the default set without
enabling DetailedMetrics, use the `AdditionalMetrics` configuration parameter. 

`DetailedMetrics` is evaluated before `EnableIndexStats` and
`EnableClusterStats`. If `DetailedMetrics` is false, setting `EnableIndexStats`
and `EnableClusterStats` to true will cause the plugin to report only those
index and cluster metrics that are included in the default set of metrics.

##### Specify secondary collection interval for index stats

This update includes a separate collection interval for index stats, specified
in `IndexInterval`. This was added because the collection of index stats in
particular can be CPU-intensive. The default setting of this interval in
[`20-elasticsearch.conf`](https://github.com/signalfx/integrations/tree/master/collectd-elasticsearch/20-elasticsearch.conf) transmits index stats every 5 minutes. 

##### Address missing metric mappings in recent versions of Elasticsearch

This update adds compatibility with more recent versions of Elasticsearch up to
2.1, in which some metric names have changed. Before this update, the plugin
would log errors that metrics could not be found. 

#### 2016-06-27: Support for basic authentication 

The plugin was updated to support basic authentication with Elasticsearch
installations. You can now supply username and password in the configuration
file for this plugin. 
