import os
from dotenv import load_dotenv
import subprocess
import datetime
import logging
from zipfile import ZipFile

load_dotenv() # Load .env file

# Configuration variables
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_DIR = "./logs"
LOG_FILE = f"{LOG_DIR}/log_{TIMESTAMP}.log"
BACKUP_DIR = "./backup"
BACKUP_FILE = f"{BACKUP_DIR}/backup_{TIMESTAMP}.sql"
COMPRESSED_FILE = f"{BACKUP_FILE}.zip"
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PSWD = os.getenv("DB_PSWD")
DB_NAME = os.getenv("DB_NAME")
SSH_USER = os.getenv("SSH_USER")
SSH_HOST = os.getenv("SSH_HOST")
SSH_PORT = os.getenv("SSH_PORT")
LOCAL_PORT = os.getenv("LOCAL_PORT")

# Ensure the necessary directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    format='%(asctime)s - [%(levelname)s] %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

# Progress flags
SSH_TUNNEL_REQUIRED = False
BACKUP_COMPLETE = False

# List of commands
# ssh_command = f"ssh {SSH_USER}@{SSH_HOST} -p {SSH_PORT}".split()
ssh_command = f"ssh -f -N -L {LOCAL_PORT}:{DB_HOST}:{DB_PORT} {SSH_USER}@{SSH_HOST} -p {SSH_PORT}".split()
backup_command = f"sudo docker run --rm mysql:latest mysqldump -h {DB_HOST} -P {DB_PORT} -u {DB_USER} -p{DB_PSWD} {DB_NAME}".split()
cleanup_command = f"pkill -f ssh.*{LOCAL_PORT}:{DB_HOST}:{DB_PORT}".split()

# Custom log-and-print function
def log_message(code, msg):
    # LOGGING CODES:
    # info - 20
    # warning - 30
    # error - 40
    # critical - 50
    # (Source: https://docs.python.org/3/library/logging.html)

    logging.log(code, msg)
    print(msg)

# Writes to backup file using backup command
def docker_backup():
    with open(BACKUP_FILE, "w") as backup_file:
        backup_process = subprocess.run(backup_command, stdout=backup_file, stderr=subprocess.PIPE)
        if backup_process.returncode != 0:
            log_message(40, backup_process.stderr.decode("utf-8"))
            return 1
        else:
            return 0

# Terminates any ongoing SSH connection
def ssh_cleanup():
    log_message(20, f"Terminating SSH conection...")
    subprocess.run(cleanup_command)

log_message(20, "Initiating backup script via Python...")

# Attempt backup with a direct connection to the MySQL server
if not SSH_TUNNEL_REQUIRED:
    log_message(20, "Attempting direct server connection...")
    if docker_backup() != 0:
        log_message(40, "Backup via direct connection failed.")
        SSH_TUNNEL_REQUIRED = True
    else:
        log_message(20, "Backup via direct connection successful.")
        BACKUP_COMPLETE = True

# Attempt backup with SSH connection
if SSH_TUNNEL_REQUIRED:
    log_message(20, "Attempting SSH connection...")
    ssh_process = subprocess.run(ssh_command, stderr=subprocess.PIPE)
    if ssh_process.returncode != 0:
        log_message(40, ssh_process.stderr.decode("utf-8"))
        log_message(40, "Failed to set up SSH connection.")
        exit(1)
    else:
        log_message(20, "SSH connection successful. Attempting to back up data...")
        if docker_backup() != 0:
            log_message(40, "Backup via SSH connection failed.")
            ssh_cleanup()
            exit(1)
        else:
            log_message(20, "Backup via SSH connection successful.")
            BACKUP_COMPLETE = True

# Compress backup file
if BACKUP_COMPLETE:
    log_message(20, "Compressing backup file...")
    with ZipFile(f"{COMPRESSED_FILE}", "w") as myzip:
        myzip.write(f"{BACKUP_FILE}")
    log_message(20, f"Compression completed: {COMPRESSED_FILE}")

# Clean up SSH tunnel if used
if SSH_TUNNEL_REQUIRED:
    ssh_cleanup()

log_message(20, "Done.")
exit(0)
