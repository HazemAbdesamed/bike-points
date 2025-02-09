#!/bin/bash
# Copyright VMware, Inc.
# SPDX-License-Identifier: APACHE-2.0

# shellcheck disable=SC1091

set -o errexit
set -o nounset
set -o pipefail

# set -o xtrace # Uncomment this line for debugging purposes

# Load libraries
. /opt/bitnami/scripts/liblog.sh
. /opt/bitnami/scripts/libbitnami.sh
. /opt/bitnami/scripts/libkafka.sh

# Load Kafka environment variables
. /opt/bitnami/scripts/kafka-env.sh

print_welcome_page

if [[ "$*" = *"/opt/bitnami/scripts/kafka/run.sh"* || "$*" = *"/run.sh"* ]]; then
    info "** Starting Kafka setup **"
    /opt/bitnami/scripts/kafka/setup.sh
    info "** Kafka setup finished! **"
fi


"$@" &

echo "checking if topic exists ..." 
# If no topic has been created, create one
if [ -z "$(kafka-topics.sh --bootstrap-server $BROKER1:$PORT1 --list)" ]; then
  echo "Creating topic..."
  /scripts/create-topic.sh
fi

tail -f /dev/null