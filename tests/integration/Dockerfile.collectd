FROM quay.io/signalfuse/collectd:latest

# Disable everything we can except elasticsearch
ENV COLLECTD_INTERVAL=3 COLLECTD_HOSTNAME=es-test DISABLE_AGGREGATION=true DISABLE_CPU=true DISABLE_CPUFREQ=true DISABLE_DF=true DISABLE_DISK=true DISABLE_DOCKER=true DISABLE_HOST_MONITORING=true DISABLE_INTERFACE=true DISABLE_LOAD=true DISABLE_MEMORY=true DISABLE_PROTOCOLS=true DISABLE_VMEM=true DISABLE_UPTIME=true

# Debian is super minimalistic
RUN apt-get update &&\
    apt-get install -yq netcat

CMD /.docker/wait_for_es
ADD tests/integration/wait_for_es /.docker/wait_for_es

## The context of the image build should be the root dir of this repo!!
ADD elasticsearch_collectd.py /usr/share/collectd/collectd-elasticsearch/
ADD tests/integration/20-elasticsearch-test.conf /etc/collectd/managed_config/
