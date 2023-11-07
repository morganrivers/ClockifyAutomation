#!/bin/bash
# Makes sure to back up aw - not this boot, but the one before, then subtract a day for good measure. 
# So every boot, we save events somewhere in case activity watch deletes our data or we reinstall it wrong, etc.

# Specify bucket id
BUCKET_ID="aw-watcher-window_snailshale"

echo "BUCKET_ID"
echo $BUCKET_ID
# Specify backup directory
BACKUP_DIR="/home/dmrivers/Documents/backup/aw_backups"

echo "BACKUP_DIR"
echo $BACKUP_DIR
# Specify last boot file location
LAST_BOOT_FILE="/home/dmrivers/Code/Debian/last_boot.txt"

echo "LAST_BOOT_FILE"
echo $LAST_BOOT_FILE
# Get current time in ISO 8601 format
END_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "END_TIME"
echo $END_TIME
# Get last boot time from the file, convert it to ISO 8601 format
# Assuming the boot time in the file is in the format like: "Thu Jun 1 16:49:13 2023"
# The 'date -u' command may need adjustment for your timezone
BOOT_TIME=$(date -u -d "$(awk '{print $1,$2,$3,$4,$5}' $LAST_BOOT_FILE)" +"%Y-%m-%dT%H:%M:%SZ")

START_TIME=$(date -u -d "${BOOT_TIME} - 24 hours" +"%Y-%m-%dT%H:%M:%SZ")

echo "BOOT_TIME"
echo $BOOT_TIME
echo "START_TIME"
echo $START_TIME

# Construct the API call
API_CALL="http://localhost:5600/api/0/buckets/${BUCKET_ID}/events?start=${START_TIME}&end=${END_TIME}"
echo "API_CALL"
echo $API_CALL

# Fetch the data and write to file
# if exists, appends (may involve duplicate data but thats okay)
curl "$API_CALL" >> "${BACKUP_DIR}/aw_backup_$(date --iso-8601).json"
