import os
from dotenv import load_dotenv
import subprocess
import datetime
import logging
from zipfile import ZipFile
from shutil import which
import requests as req
import platform
from time import sleep
import sys
import textwrap

load_dotenv() # Load .env file

# Configuration variables
ARGS = sys.argv[1:] if len(sys.argv) > 1 else None
CWD = os.path.dirname(os.path.abspath(sys.argv[0]))
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_DIR = f"{CWD}/logs"
LOG_FILE = f"{LOG_DIR}/log_{TIMESTAMP}.log"
BACKUP_DIR = f"{CWD}/backup"
BACKUP_FILE = f"{BACKUP_DIR}/backup_{TIMESTAMP}.sql"
COMPRESSED_FILE = f"{BACKUP_FILE}.zip"
IS_WINDOWS = True if platform.system() == "Windows" else False
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PSWD = os.getenv("DB_PSWD")
DB_NAME = os.getenv("DB_NAME")
SSH_USER = os.getenv("SSH_USER")
SSH_HOST = os.getenv("SSH_HOST")
SSH_PORT = os.getenv("SSH_PORT")
LOCAL_PORT = os.getenv("LOCAL_PORT")
MYSQL_VRSN = os.getenv("MYSQL_VRSN")

# List of commands
# ssh_command = f"ssh {SSH_USER}@{SSH_HOST} -p {SSH_PORT}".split()
ssh_command = f"ssh -f -N -L {LOCAL_PORT}:{DB_HOST}:{DB_PORT} {SSH_USER}@{SSH_HOST} -p {SSH_PORT}".split()
backup_command = f"{"" if IS_WINDOWS else "sudo "}docker run --rm mysql:{MYSQL_VRSN} mysqldump -h {DB_HOST} -P {DB_PORT} -u {DB_USER} -p{DB_PSWD} {DB_NAME}".split()
cleanup_command = f"pkill -f ssh.*{LOCAL_PORT}:{DB_HOST}:{DB_PORT}".split()

# Helper functions
def render_red(text): # Returns "red" text using the necessary ANSI escape sequences
    return f"\033[91m{text}\033[00m"

def render_yellow(text): # Returns "yellow" text using the necessary ANSI escape sequences
    return f"\033[93m{text}\033[00m"

def print_typewriter(text):
    for char in text:
        print(char, end="")
        sys.stdout.flush()
        speed = 2
        if ARGS and "-t" in ARGS:
            i = ARGS.index("-t")
            if len(ARGS) > i + 1 and ARGS[i + 1].isnumeric():
                speed = ARGS[i + 1]
        sleep(0.01 * int(speed))
    print()

def log_message(code, msg): # Custom log-and-print function
    # LOGGING CODES:
    # info - 20
    # warning - 30
    # error - 40
    # critical - 50
    # (Source: https://docs.python.org/3/library/logging.html)

    logging.log(code, msg)

    if ARGS and "-q" in ARGS:
        pass
    elif ARGS and "-t" in ARGS:
        if code == 30:
            print_typewriter(render_yellow(msg))
        elif code == 40 or code == 50:
            print_typewriter(render_red(msg))
        else:
            print_typewriter(msg)
    else:
        if code == 30:
            print(render_yellow(msg))
        elif code == 40 or code == 50:
            print(render_red(msg))
        else:
            print(msg)

def command_check(cmd): # Checks if a specific command exists
    if which(cmd) == None:
        log_message(40, f"The command \"{cmd}\" does not exist on your machine.")
        return 1
    else:
        return 0

def docker_backup(): # Writes to backup file using backup command
    # 1. Validate the specified MySQL image tag
    url = f"https://registry.hub.docker.com/v2/repositories/library/mysql/tags/{MYSQL_VRSN}" # Endpoint for MySQL tags via Docker Hub
    res = req.get(url)

    if res.status_code != 200:
        log_message(40, f"Error fetching tag '{MYSQL_VRSN}'. (Status Code: {res.status_code})")
        exit(1)
        
    # 2. Backup database via Docker
    with open(BACKUP_FILE, "w") as backup_file:
        backup_process = subprocess.run(backup_command, stdout=backup_file, stderr=subprocess.PIPE)
        if backup_process.returncode != 0:
            log_message(40, backup_process.stderr.decode("utf-8"))
            return 1
        else:
            return 0
        
def ssh_cleanup(): # Terminates any ongoing SSH connection
    log_message(20, "Terminating SSH connection...")
    sleep(2)
    subprocess.run(cleanup_command)

# Main execution
def main():
    if ARGS and "-h" in ARGS:
        print(textwrap.dedent(
            '''\
            MySQL Backup Script (Python)

            Options:
                -h        print script info and list of available options
                -q        quiet mode
                -t <int>  typewriter effect that prints a character every <int> centisecond; <int> is 2 by default\
            '''
            ))
        exit(0)

    print(render_yellow(f"NOTE: Once the script terminates (with or without errors), the log file can be located here: {LOG_FILE}"))
    sleep(2)

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
    SSH_TUNNEL_REQUIRED = True if all(var != None for var in [LOCAL_PORT, DB_HOST, DB_PORT, SSH_USER, SSH_HOST, SSH_PORT]) else False
    BACKUP_COMPLETE = False

    # NOTE: all() (used above) returns True if all the items in the iterable fit the boolean criteria, and returns False otherwise

    log_message(20, "Initiating backup script via Python...")
    sleep(2)
    
    log_message(20, "Checking for required programs...")
    sleep(2)
    if command_check("ssh") != 0 or command_check("docker") != 0:
        exit(1)
    else:
        log_message(20, "Program check successful.")

    if SSH_TUNNEL_REQUIRED == False:
        log_message(30, "Incomplete SSH configuration.")

    # Attempt backup with SSH connection
    if SSH_TUNNEL_REQUIRED:
        log_message(20, "Attempting SSH connection...")
        sleep(2)
        ssh_process = subprocess.run(ssh_command, stderr=subprocess.PIPE)
        if ssh_process.returncode != 0:
            log_message(40, ssh_process.stderr.decode("utf-8"))
            log_message(40, "Failed to set up SSH connection.")
            SSH_TUNNEL_REQUIRED = False
        else:
            log_message(20, "SSH connection successful. Attempting to back up data...")
            sleep(2)
            if docker_backup() != 0:
                log_message(40, "Backup via SSH connection failed.")
                SSH_TUNNEL_REQUIRED = False
            else:
                log_message(20, "Backup via SSH connection successful.")
                BACKUP_COMPLETE = True
            ssh_cleanup()

    # Attempt backup with a direct connection to the MySQL server
    if not SSH_TUNNEL_REQUIRED:
        log_message(20, "Attempting direct server connection...")
        sleep(2)
        if docker_backup() != 0:
            log_message(40, "Backup via direct connection failed.")
            exit(1)
        else:
            log_message(20, "Backup via direct connection successful.")
            BACKUP_COMPLETE = True

    # Compress backup file
    if BACKUP_COMPLETE:
        log_message(20, "Compressing backup file...")
        sleep(2)
        with ZipFile(f"{COMPRESSED_FILE}", "w") as myzip:
            myzip.write(f"{BACKUP_FILE}")
        log_message(20, f"Compression completed: {COMPRESSED_FILE}")

    log_message(20, "Done.")
    exit(0)

if __name__ == "__main__":
    # NOTE: Code to be executed was reformatted so that it is not ran when this file is imported
    main()
