#! /bin/bash
# File: feline.sh
# Author: Gael Marcadet <gael.marcadet@limos.fr>
# Description: Launch the FELINE demo.

# stop on failure
set -e


# launching in docker
echo "[+] Launching FELINE in Docker Environement"
sudo docker-compose up
