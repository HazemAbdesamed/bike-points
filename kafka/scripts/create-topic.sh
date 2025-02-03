kafka-topics.sh --bootstrap-server $BROKER1:$PORT1 --create --topic $TOPIC_DATA --replication-factor 1 --partitions 1;

# Set the retention time of the messages for this topic to 48 hours
kafka-configs.sh --bootstrap-server $BROKER1:$PORT1 --alter --entity-type topics --entity-name $TOPIC_DATA --add-config retention.ms=172800000