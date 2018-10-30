#!/usr/bin/env python

import httplib
import json
from time import time, sleep

# Quick and dirty integration test for multi-cluster support in one collectd
# instance. This test script is intended to be run with docker-compose with the
# provided docker-compose.yml configuration.

# This is not very flexible but could be expanded to support other types of
# integration tests if so desired.

VERSIONS_TESTED_WITH_METRICS = {
    '1.7.6' : ['indices.indexing.index-total'],
    '2.4.5' : ['indices.cache.filter.evictions'],
    '5.3.2' : ['indices.cache.filter.evictions'],
    '5.6.3' : ['indices.cache.filter.evictions'],
}
TIMEOUT_SECS = 60


def get_metric_data():
    # Use httplib instead of requests so we don't have to install stuff with pip
    conn = httplib.HTTPConnection("fake_sfx", 8080)
    conn.request("GET", "/")
    resp = conn.getresponse()
    conn.close()
    return json.loads(resp.read())


def wait_for_metrics_from_each_cluster():
    start = time()
    for cluster in VERSIONS_TESTED_WITH_METRICS:
        c = 'es-%s' % (cluster,)
        print 'Waiting for metrics from cluster %s...' % (c,)
        eventually_true(lambda: any([c in m.get('plugin_instance') for m in get_metric_data()]),
                        TIMEOUT_SECS - (time() - start))
        print 'plugin_instance Found!'
        for metric in VERSIONS_TESTED_WITH_METRICS.get(cluster):
            print 'Waiting for metric: %s from cluster %s...' % (metric, c)
            eventually_true(lambda: any([metric in str(m.get('type_instance')) for m in get_metric_data()]),
                            TIMEOUT_SECS - (time() - start))

            print 'metric: %s Found! from cluster: %s' % (metric, c)


def eventually_true(f, timeout_secs):
    start = time()
    while True:
        try:
            assert f()
        except AssertionError:
            if time() - start > timeout_secs:
                raise
            sleep(0.5)
        else:
            break


if __name__ == "__main__":
    wait_for_metrics_from_each_cluster()
