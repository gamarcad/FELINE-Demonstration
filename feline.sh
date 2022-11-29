#! /bin/bash
# File: feline.sh
# Author: Gael Marcadet <gael.marcadet@limos.fr>
# Description: Launch the FELINE demo.

# stop on failure
set -e


# checks the required dependancies
if [[ -z $(which docker) || -z $(which docker-compose) ]]; then
    read -p "Docker is currently not installed, can I do it for you?" -n 1 -r
    echo    # (optional) move to a new line
    if [[ ! $REPLY =~ ^[Yy]$ ]]
    then
        sudo apt-get update
        read -p "Have you already install docker on this computer?" -n 1 -r
        echo    # (optional) move to a new line
        if [[ ! $REPLY =~ ^[Yy]$ ]]
        then
            sudo apt-get install ca-certificates curl gnupg lsb-release
            sudo mkdir -p /etc/apt/keyrings
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            sudo apt-get update
        fi
        sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
        echo "Everything is installed. I now execute a command to check if docker is running correctly."
        sudo docker run hello-world
    fi
else
    echo "Docker and Docker-composer are installed."
fi

# if not data folder in the location, download it
if [[ ! -e linear-api/data ]]; then
    echo "I cannot see the data folder (./linear-api/data), so I will download it from a drive."
    cd linear-api
    ./download-data.sh
    cd ..
else
    echo "The data folder (./linear-api/data) has been localized."
fi


# launch FELINE
if [[ "$1" == '--prod' ]]; then
    echo "Launching FELINE in production mode"
    ln -s docker-compose-prod.yml docker-compose.yml
else
    echo "Launching FELINE in development mode"
fi

docker-compose up

