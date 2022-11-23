#! /bin/bash
# File: feline.sh
# Author: Gael Marcadet <gael.marcadet@limos.fr>
# Description: Launch the FELINE demo.

# stop on failure
set -e

# if not data folder in the location, download it
if [[ ! -e linear-api/data ]]; then
    echo "No data folder found: downloading it from the cloud..."
    cd linear-api
    ./download-data.sh
    cd ..
fi

# launching in docker
echo "[+] Launching FELINE in Docker Environement"
sudo docker-compose up
