#!/bin/bash
# Makes sure to back up AW - not this boot, but the one before, then subtract a day for good measure.
# So every boot, we save events somewhere in case ActivityWatch deletes our data or we reinstall it wrong, etc.

# Specify window and AFK bucket IDs
WINDOW_BUCKET_ID="aw-watcher-window_snailshale"
AFK_BUCKET_ID="aw-watcher-afk_snailshale"

echo "Window BUCKET_ID: $WINDOW_BUCKET_ID"
echo "AFK BUCKET_ID: $AFK_BUCKET_ID"

# Specify backup directory
BACKUP_DIR="/home/dmrivers/Documents/backup/aw_backups"

echo "BACKUP_DIR: $BACKUP_DIR"

# Specify last boot file location
LAST_BOOT_FILE="/home/dmrivers/Code/Debian/last_boot.txt"

echo "LAST_BOOT_FILE: $LAST_BOOT_FILE"

# Get current time in ISO 8601 format
END_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "END_TIME: $END_TIME"

# Get last boot time from the file, convert it to ISO 8601 format
# Assuming the boot time in the file is in the format like: "Thu Jun 1 16:49:13 2023"
# The 'date -u' command may need adjustment for your timezone
BOOT_TIME=$(date -u -d "$(awk '{print $1,$2,$3,$4,$5}' $LAST_BOOT_FILE)" +"%Y-%m-%dT%H:%M:%SZ")

START_TIME=$(date -u -d "${BOOT_TIME} - 24 hours" +"%Y-%m-%dT%H:%M:%SZ")

echo "BOOT_TIME: $BOOT_TIME"
echo "START_TIME: $START_TIME"

# Construct the API call for window events
WINDOW_API_CALL="http://localhost:5600/api/0/buckets/${WINDOW_BUCKET_ID}/events?start=${START_TIME}&end=${END_TIME}"
echo "Window API_CALL: $WINDOW_API_CALL"

# Fetch the window data and write to file
# if exists, appends (may involve duplicate data but that's okay)
curl "$WINDOW_API_CALL" >> "${BACKUP_DIR}/aw_backup_window_$(date --iso-8601).json"

# Construct the API call for AFK events
AFK_API_CALL="http://localhost:5600/api/0/buckets/${AFK_BUCKET_ID}/events?start=${START_TIME}&end=${END_TIME}"
echo "AFK API_CALL: $AFK_API_CALL"

# Fetch the AFK data and write to file
# if exists, appends (may involve duplicate data but that's okay)
curl "$AFK_API_CALL" >> "${BACKUP_DIR}/aw_backup_afk_$(date --iso-8601).json"
