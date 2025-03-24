# Automated MySQL Database Backup Script for Cross-Platform Remote Clients <br> ![mysql](https://img.shields.io/badge/MySQL-005C84?style=for-the-badge&logo=mysql&logoColor=white) ![docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white) ![python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue) ![shell-script](https://img.shields.io/badge/Shell_Script-121011?style=for-the-badge&logo=gnu-bash&logoColor=white) ![ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)

## Project Description
The goal of this project was to develop a robust and cross-platform script that automates the backup of a remote MySQL database. The script runs on a client machine (Linux, macOS, or Windows) and backs up a MySQL database hosted on a remote server. The client machine has MySQL installed via a Docker image and may need to connect to the remote server via SSH if direct MySQL access is not available. The script handles errors gracefully, logs its activities, and stores backups securely on the client machine.

## Dependencies
Client:
- Windows, macOS, or Linux
- Python3
- Docker
- SSH

Server:
- Linux (preferably)
- MySQL Server
- SSH
