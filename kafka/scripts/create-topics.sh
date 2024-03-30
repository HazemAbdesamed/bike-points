kafka-topics.sh --bootstrap-server $BROKER1:$PORT1 --create --topic $TOPIC_DATA --replication-factor 1 --partitions 1;

kafka-topics.sh --bootstrap-server $BROKER1:$PORT1 --create --topic $TOPIC_METRICS --replication-factor 1 --partitions 1;