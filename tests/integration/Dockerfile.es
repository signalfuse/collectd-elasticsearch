FROM elasticsearch:ES_VERSION

ENV ELASTICSEARCH_VERSION=ES_VERSION

ENV ELASTICSEARCH_DEB_VERSION=ES_VERSION

CMD /set_cluster_name

ADD set_cluster_name /set_cluster_name
