# @ -> root directory
import script # @/script.py
import subprocess
import platform

# Test test
def test_check():
    assert 1 == 1

# Check if the remote server is reachable
def test_ping():
    # NOTE: In order to ping a specific number of times, use `ping -n` for Windows and `ping -c` for macOS and Linux
    is_windows = True if platform.system() == "Windows" else False
    ping_command = f"ping {"-n" if is_windows else "-n"} 5 {script.SSH_HOST}".split()
    assert subprocess.run(ping_command).returncode == 0

# Check if the value of the database user is valid
def test_db_user():
    assert not (script.DB_USER == "") and not (script.DB_USER == None)