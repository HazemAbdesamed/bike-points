#!/usr/bin/env bash
## copied from: https://github.com/docker-library/postgres/pull/496#issue-358838955
set -Eeo pipefail

echo "🐘 custom-entry-point"
# Example using the functions of the postgres entrypoint to customize startup to always run files in /always-initdb.d/

source "$(which docker-entrypoint.sh)"

docker_setup_env
docker_create_db_directories
# assumption: we are already running as the owner of PGDATA

# This is needed if the container is started as `root`
#if [ "$1" = 'postgres' ] && [ "$(id -u)" = '0' ]; then
if [ "$(id -u)" = '0' ]; then
  exec gosu postgres "$BASH_SOURCE" "$@"
fi


if [ -z "$DATABASE_ALREADY_EXISTS" ]; then
  echo "🐘 no existing db "
  docker_verify_minimum_env
  docker_init_database_dir
  pg_setup_hba_conf

  # only required for '--auth[-local]=md5' on POSTGRES_INITDB_ARGS
  export PGPASSWORD="${PGPASSWORD:-$POSTGRES_PASSWORD}"

  docker_temp_server_start "$@" -c max_locks_per_transaction=256
  docker_setup_db
  docker_process_init_files /docker-entrypoint-initdb.d/*
  docker_temp_server_stop
else
  echo "🐘 a db exists"
  docker_temp_server_start "$@"
  docker_process_init_files /docker-entrypoint-initdb.d/*
  docker_temp_server_stop
fi

echo "🐘 .. starting!"
exec postgres "$@"