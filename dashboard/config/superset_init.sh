#!/bin/bash

# create Admin user, you can read these values from env or anywhere else possible
superset fab create-admin --username "$SUPERSET_ADMIN_USERNAME" --firstname Superset --lastname Admin --email "$SUPERSET_ADMIN_EMAIL" --password "$SUPERSET_ADMIN_PASSWORD"

# Upgrading Superset metastore
superset db upgrade

# setup roles and permissions
superset superset init 

# Import the dashboard
echo "Importing the dashboard..." & 
superset import-dashboards --username $SUPERSET_ADMIN_USERNAME -p /app/superset-dashboard-data.zip

# Starting server
/bin/sh -c /usr/bin/run-server.sh