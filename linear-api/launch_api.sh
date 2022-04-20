# file: launch_api.sh
# description: utility used to launch the API

# stop the program at the first failure
set -e

# launch the program
python3 -m uvicorn api:app --reload