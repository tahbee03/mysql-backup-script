import os
from dotenv import load_dotenv
import subprocess
import datetime
import logging
from zipfile import ZipFile

load_dotenv() # Load .env file

# Configuration variables
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = f"./logs/log_{TIMESTAMP}.log"
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

# Ensure backup directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    format='%(asctime)s - [%(levelname)s] %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

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

log_message(20, "Initiating script...")

SSH_TUNNEL_REQUIRED = False

# ssh_command = f"ssh {SSH_USER}@{SSH_HOST} -p {SSH_PORT}".split()

# Attempt backup with a direct connection to the MySQL server
log_message(20, "Attempting direct server connection...")
with open(BACKUP_FILE, "w") as backup_file:
    backup_command = f"docker run --rm mysql:latest mysqldump -h {DB_HOST} -P {DB_PORT} -u {DB_USER} -p{DB_PSWD} {DB_NAME}".split()
    process1 = subprocess.run(backup_command, stdout=backup_file, stderr=subprocess.PIPE)
    if process1.returncode != 0:
        log_message(40, process1.stderr.decode("utf-8"))
        log_message(40, "Backup via direct connection failed.")
        SSH_TUNNEL_REQUIRED = True
    else:
        log_message(20, "Backup via direct connection successful.")

# Attempt backup with SSH connection
# FIXME: The terminal becomes unresponsive whenever the SSH tunnel gets sent to the background
if SSH_TUNNEL_REQUIRED:
    log_message(20, "Attempting SSH connection...")
    DB_HOST="127.0.0.1"
    ssh_command = f"ssh -v -f -N -L {LOCAL_PORT}:{DB_HOST}:{DB_PORT} {SSH_USER}@{SSH_HOST} -p {SSH_PORT}".split()
    backup_command = f"docker run --rm mysql:latest mysqldump -h {DB_HOST} -P {DB_PORT} -u {DB_USER} -p{DB_PSWD} {DB_NAME}".split()
    process2 = subprocess.run(ssh_command)
    if process2.returncode != 0:
        log_message(40, process2.stderr.decode("utf-8"))
        log_message(40, "Failed to set up SSH connection.")
        exit(1)
    else:
        log_message(20, "SSH connection successful. Attempting to back up data...")
        with open(BACKUP_FILE, "w") as backup_file:
            process3 = subprocess.run(backup_command, stdout=backup_file, stderr=subprocess.PIPE)
            if process3.returncode != 0:
                log_message(40, process3.stderr.decode("utf-8"))
                log_message(40, "Backup via SSH connection failed.")
                exit(1)
            else:
                log_message(20, "Backup via SSH connection successful.")

# Compress backup file
log_message(20, "Compressing backup file...")
with ZipFile(f"{COMPRESSED_FILE}", "w") as myzip:
    myzip.write(f"{BACKUP_FILE}")

log_message(20, f"Compression completed: {COMPRESSED_FILE}")

# Clean up SSH tunnel if used
if SSH_TUNNEL_REQUIRED:
    log_message(20, f"Terminating SSH conection...")
    cleanup_command = f"pkill -f ssh.*{LOCAL_PORT}:{DB_HOST}:{DB_PORT}".split()
    subprocess.run(cleanup_command)

exit(0)
