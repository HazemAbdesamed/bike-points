#!/bin/bash
# Copyright VMware, Inc.
# SPDX-License-Identifier: APACHE-2.0

# shellcheck disable=SC1091

set -o errexit
set -o nounset
set -o pipefail
#set -o xtrace

# Load libraries
. /opt/bitnami/scripts/libbitnami.sh
. /opt/bitnami/scripts/libcassandra.sh

# Load Cassandra environment variables
. /opt/bitnami/scripts/cassandra-env.sh

print_welcome_page

if is_positive_int "$CASSANDRA_DELAY_START_TIME" && [[ "$CASSANDRA_DELAY_START_TIME" -gt 0 ]]; then
    info "** Delaying Cassandra start by ${CASSANDRA_DELAY_START_TIME} seconds **"
    sleep "$CASSANDRA_DELAY_START_TIME"
fi

if [[ "$*" = *"/opt/bitnami/scripts/cassandra/run.sh"* || "$*" = *"/run.sh"* ]]; then
    info "** Starting Cassandra setup **"
    /opt/bitnami/scripts/cassandra/setup.sh
    info "** Cassandra setup finished! **"
fi

echo ""
exec "$@"  &

# Execute CQL script to create the keyspace and the table if they don't exist 
echo "setting up the db and the table if they don't exist"
cqlsh -u $CASSANDRA_USER -p $CASSANDRA_PASSWORD  -f /scripts/init.cql

tail -f /dev/null