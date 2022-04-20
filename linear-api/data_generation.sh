#!/bin/bash

# Stop at the first error
set -e

DATA_FOLDER=debug

# Generate data for security comparison purpose
python3 main.py data --instances debug_instances.json --mode full --output $DATA_FOLDER/data_M_{M}_N_{N}_d_{d}_K_{K}.json

ITERATION=10
INPUTS=$(find $DATA_FOLDER/ | grep json)
python3 main.py benchmark\
    --inputs $INPUTS\
    --output results\
    --iteration $ITERATION