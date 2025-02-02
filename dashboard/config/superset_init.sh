#!/bin/bash

# create Admin user
superset fab create-admin --username "$SUPERSET_ADMIN_USERNAME" --firstname Superset --lastname Admin --email "$SUPERSET_ADMIN_EMAIL" --password "$SUPERSET_ADMIN_PASSWORD"

# Upgrading Superset metastore
superset db upgrade

# setup roles and permissions
superset superset init 

# Path to the original zip file
ZIP_FILE=/app/superset-dashboard-data.zip
TEMP_DIR=/tmp/dashboard/

# # Extract the zip file
echo "Unzipping the dashboard folder..."
unzip $ZIP_FILE -d $TEMP_DIR

# Replace environment variables in YAML files
echo "Replacing environment variables in YAML files..."
find $TEMP_DIR -type f \( -name "cassandra.yaml" -o -name "postgres.yaml" \) | while read -r file; do
    sed -i "s/\$TRINO_INTERNAL_PORT/$TRINO_INTERNAL_PORT/g" "$file"
done

# Re-zip the folder
echo "Re-zipping the folder..."
cd $TEMP_DIR
DASHBOARD_TO_IMPORT=$TEMP_DIR/superset-dashboard-data-to-import.zip
zip -r $DASHBOARD_TO_IMPORT .
cd /app
# Import the dashboard
echo "Importing the dashboard..."
superset import-dashboards --username $SUPERSET_ADMIN_USERNAME -p $DASHBOARD_TO_IMPORT

# Clean up
echo "Cleaning up..."
rm -rf $TEMP_DIR

# Starting server
echo "Starting the server..."
/bin/sh -c /usr/bin/run-server.sh


# Keep the script running to prevent the container from exiting
tail -f /dev/null