#!/bin/bash

# Configuration Variables
source .env # Load sensitive info from .env file
BACKUP_DIR="./backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"
COMPRESSED_FILE="$BACKUP_FILE.gz"
LOG_FILE="$BACKUP_DIR/log_$TIMESTAMP.log"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Function to log messages
log_message() {
echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Check if SSH tunneling is needed
SSH_TUNNEL_REQUIRED=true
if ! nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; then
SSH_TUNNEL_REQUIRED=true
log_message "Direct MySQL connection failed."
fi

# Set up SSH tunnel if required
if [ "$SSH_TUNNEL_REQUIRED" = true ]; then
log_message "Setting up SSH tunnel..."
LOCAL_PORT=3307
ssh -f -N -L "$LOCAL_PORT:$DB_HOST:$DB_PORT" "$SSH_USER@$SSH_HOST" -p "$SSH_PORT"
if [ $? -ne 0 ]; then
log_message "ERROR: Failed to set up SSH tunnel."
exit 1
fi
# DB_HOST="127.0.0.1"
# DB_PORT="$LOCAL_PORT"
fi

# Run mysqldump inside Docker container
log_message "Starting database backup..."
sudo docker run --rm mysql:latest mysqldump -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PSWD" "$DB_NAME" > "$BACKUP_FILE" 2>> "$LOG_FILE"
if [ $? -ne 0 ]; then
log_message "ERROR: mysqldump failed."

# Clean up SSH tunnel if used
if [ "$SSH_TUNNEL_REQUIRED" = true ]; then
pkill -f "ssh.*$LOCAL_PORT:$DB_HOST:$DB_PORT"
fi
exit 1
fi

# Compress the backup file
log_message "Compressing backup file..."
gzip "$BACKUP_FILE"
if [ $? -ne 0 ]; then
log_message "ERROR: Compression failed."
exit 1
fi

# Clean up SSH tunnel if used
if [ "$SSH_TUNNEL_REQUIRED" = true ]; then
pkill -f "ssh.*$LOCAL_PORT:$DB_HOST:$DB_PORT"
fi

log_message "Backup completed successfully: $COMPRESSED_FILE"