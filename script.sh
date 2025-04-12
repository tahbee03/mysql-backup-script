#!/bin/bash

# Configuration variables
source .env # Load sensitive info from .env file
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="./logs"
LOG_FILE="$LOG_DIR/log_$TIMESTAMP.log"
BACKUP_DIR="./backup"
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"
COMPRESSED_FILE="$BACKUP_FILE.gz"
# DB_HOST -> retrieved from .env
# DB_PORT -> retrieved from .env
# DB_USER -> retrieved from .env
# DB_PSWD -> retrieved from .env
# DB_NAME -> retrieved from .env
# SSH_USER -> retrieved from .env
# SSH_HOST -> retrieved from .env
# SSH_PORT -> retrieved from .env
# LOCAL_PORT -> retrieved from .env

# Ensure the necessary directories exist
mkdir -p "$LOG_DIR"
mkdir -p "$BACKUP_DIR"

# Progress flags
SSH_TUNNEL_REQUIRED=false
BACKUP_COMPLETE=false

# Function to log messages
log_message() {
    echo $1
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

log_message "Initiating backup script via Bash..."

# Check if SSH tunneling is needed
log_message "Attempting direct server connection..."
if ! nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; then
    SSH_TUNNEL_REQUIRED=true
    log_message "Direct connection to MySQL server failed."
fi

# Set up SSH tunnel if required
if [ "$SSH_TUNNEL_REQUIRED" = true ]; then
    log_message "Attempting SSH connection..."
    ssh -f -N -L "$LOCAL_PORT:$DB_HOST:$DB_PORT" "$SSH_USER@$SSH_HOST" -p "$SSH_PORT" 2>> "$LOG_FILE"
    if [ $? -ne 0 ]; then
        log_message "Failed to set up SSH connection."
        exit 1
    fi
fi

# Run mysqldump inside Docker container
log_message "Starting database backup..."
sudo docker run --rm mysql:latest mysqldump -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PSWD" "$DB_NAME" > "$BACKUP_FILE" 2>> "$LOG_FILE"
if [ $? -ne 0 ]; then
    log_message "Failed to backup data."
    exit 1
else
    BACKUP_COMPLETE=true
fi

# Compress the backup file
if [ "$BACKUP_COMPLETE" = true ]; then
    log_message "Compressing backup file..."
    gzip "$BACKUP_FILE" 2>> "$LOG_FILE"
fi
if [ $? -ne 0 ]; then
    log_message "Failed to compress backup data."
    exit 1
fi

# Clean up SSH tunnel if used
if [ "$SSH_TUNNEL_REQUIRED" = true ]; then
    log_message "Terminating SSH connection..."
    pkill -f "ssh.*$LOCAL_PORT:$DB_HOST:$DB_PORT"
fi

log_message "Backup completed successfully: $COMPRESSED_FILE"
log_message "Done."
