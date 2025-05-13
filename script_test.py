# @ -> root directory
import script
import subprocess
import platform
import os
from dotenv import load_dotenv

load_dotenv() # Load .env file

# Test test
def test_check():
    assert 1 == 1

# Check if the remote server is reachable
def test_ping():
    # NOTE: In order to ping a specific number of times, use `ping -n` for Windows and `ping -c` for macOS and Linux
    is_windows = True if platform.system() == "Windows" else False
    ping_command = f"ping {"-n" if is_windows else "-c"} 3 {os.getenv("SSH_HOST")}".split()
    assert subprocess.run(ping_command).returncode == 0

# Check if the value of the database user from .env is valid
def test_db_user_1():
    assert not (os.getenv("DB_USER") == "") and not (os.getenv("DB_USER") == None)

# Check if the value of the database user from script.py is valid
def test_db_user_2():
    assert not (script.DB_USER == "") and not (script.DB_USER == None)

def test_command_check_func():
    assert script.command_check("dummycmd") == 1