# Automated MySQL Database Backup Script for Cross-Platform Remote Clients  
![mysql](https://img.shields.io/badge/MySQL-005C84?style=for-the-badge&logo=mysql&logoColor=white) ![docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white) ![python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue) ![shell script](https://img.shields.io/badge/Shell_Script-121011?style=for-the-badge&logo=gnu-bash&logoColor=white) ![ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white) ![google cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)

## Project Description
The goal of this project was to develop a robust and cross-platform script that automates the backup of a remote MySQL database. The script runs on a client machine (Linux, macOS, or Windows) and backs up a MySQL database hosted on a remote server. The client machine has MySQL installed via a Docker image and may need to connect to the remote server via SSH if direct MySQL access is not available. The script handles errors gracefully, logs its activities, and stores backups securely on the client machine.

## Project Infrastructure
Client:
- Windows, macOS, or Linux
- Python3 + PIP
- Docker
- SSH

Server:
- Linux (preferably)
- MySQL Server
- SSH

## Setup
In order to ensure the script works efficiently and seamlessly, make sure that the following steps are done first on your client machine. Once the setup is complete, the steps do not need to be done again.

1. Ensure that `ssh-copy-id` is installed. This reduces the hassle of manually copying SSH keys to the remote server. (NOTE: `ssh-keygen` should be available by default on all operating systems.)

    macOS:
    ```bash
    $ brew install ssh-copy-id
    ```

    Windows:  
    `ssh-copy-id` is not available as a usable program for Windows. As an alternative, you can either use Windows Subsystem for Linux (WSL) or PuTTY to use the command via a Windows machine.

    Linux:  
    `ssh-copy-id` is available by default for Linux.

2. Generate an SSH key pair with `ssh-keygen`. This will allow you to securely SSH into the remote server without a password prompt. Additional options for this command can be found [here](https://man7.org/linux/man-pages/man1/ssh-keygen.1.html).

    ```bash
    $ ssh-keygen
    ```

    The output that follows should look like this after pressing the Enter key several times:
    ```text
    Generating public/private ed25519 key pair.
    Enter file in which to save the key (/home/<user>/.ssh/id_ed25519): 
    Enter passphrase (empty for no passphrase): 
    Enter same passphrase again: 
    Your identification has been saved in /home/<user>/.ssh/id_ed25519
    Your public key has been saved in /home/<user>/.ssh/id_ed25519.pub
    ```

    The file name and passphrase (aka password) are optional. If a file name is entered, the keys will be stored in the directory where `ssh-keygen` was used. Provide a full path instead if you want the keys to be stored in a specific location.

    Note that the public key ends with `.pub`; the private key has the same name without the `.pub` suffix.

3. Copy the public key to the remote host with `ssh-copy-id`. Use of this command automatically appends the public key to the file `.../<user>/.ssh/authorized_keys` on the remote server. **Do not share the private key.**

    ```bash
    $ ssh-copy-id <user>@<host>
    ```

    If your client machine has multiple SSH key pairs and/or your keys do not follow the default naming conventions, use the `-i` flag to specify the path of the public key you would like to copy.
    ```bash
    $ ssh-copy-id -i <public_key_path> <user>@<host>
    ```

    In the case where `ssh-copy-id` cannot be used, the public key can be manually copied to the remote server with the following:
    ```bash
    $ cat <public_key_path> | ssh <user>@<host> "cat >> ~/.ssh/authorized_keys"
    ```

4. If you are running the python script, ensure that the necessary dependencies are installed with the following command:

    ```bash
    $ pip install -r requirements.txt
    ```

## Testing (Python)
After the project setup has been done, the Python script can be tested with the following:

```bash
$ pytest
```

NOTE: Ensure that this is ran from the root directory so that all written tests are detected.

## Options (Python)
`-c`: upload backup file to the cloud via Google Cloud Storage (GCS)  
`-h`: print script info and list of available options  
`-q`: quiet mode  
`-t <int>`: typewriter effect that prints a character every `<int>`  centisecond; `<int>` is 2 by default

NOTE: The options can be provided in any order. However, `-h` takes precedence over all other options and terminates the script immediately after printing info.