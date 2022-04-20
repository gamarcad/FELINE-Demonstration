from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api_model import Configuration
from file import JSONFileWrapper
from recording import Recording, SYNC_VERSIONS
import json
from functools import lru_cache

# starting by reading the recording
API_CONFIGURATION_FILE = "api.conf.json"
with open( API_CONFIGURATION_FILE ) as file:
    # read the configuration file
    print("[*] Reading the configuration file from", API_CONFIGURATION_FILE)
    configuration = json.loads("".join(file.readlines()))
    print("[+] Configuration load")

    # read fragements.json
    DATA_DIRECTORY = configuration["data-directory"]
    FRAGMENTS_FILENAME = DATA_DIRECTORY + "/results/fragments.json"
    fragments_file = JSONFileWrapper(FRAGMENTS_FILENAME)
    fragments = fragments_file.read()

    list_N = set()
    list_K = set()
    list_M = set()
    list_d = set()

    for input_filename, input_entry in fragments.items():
        list_N.add(input_entry["input"]["N"])
        list_K.add(input_entry["input"]["K"])
        list_M.add(input_entry["input"]["M"])
        list_d.add(input_entry["input"]["d"])

    list_N = sorted(list_N)
    list_K = sorted(list_K)
    list_M = sorted(list_M)

    possible_configurations = {
        "list_N": list_N,
        "list_K": list_K,
        "list_M": list_M,
        "list_d": list_d,
    }


app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
@lru_cache
def home(): return "No Failure"



@lru_cache()
def read_recording_from_parameters( M, K, N, d ):
    for input_filename, input_entry in fragments.items():
        input = input_entry['input']
        if input["M"] == M and input["K"] == K and input["N"] == N and input["d"] == d:
            output = DATA_DIRECTORY + "/" + input_entry["output"]
            recording = Recording.from_file( output )
            return recording
    raise Exception("Unkown configuration")







@app.get("/api/parameters/values")
def param_values():
    return possible_configurations

@app.get("/api/turn/rewards")
def home(  M : int, N : int, K : int, d : int, algorithm : str, algorithm_security : str, algorithm_synchronization : str ):
    """
    URL: /turn/rewards
    Description: Returns the cumulative rewards at each time step.

    """

    recording = read_recording_from_parameters(
        M=M,
        N=N,
        K=K,
        d=d,
    )
    return recording.get_rewards_by_turn( algorithm, algorithm_security, algorithm_synchronization )


@app.get("/api/cumulative-execution-time/sync")
def times( M : int, N : int, K : int, d : int, algorithm : str, algorithm_security : str ):
    """
    Description: Return the time at each time step.
    """
    recording = read_recording_from_parameters(
        M=M,
        K=K,
        N=N,
        d=d,
    )

    return recording.get_cumulative_time_by_sync(
        algorithm=algorithm,
        algorithm_security=algorithm_security
    )

def get_algorithm_version(algorithm_security, algorithm_synchronization):
    return f"{algorithm_security}.{algorithm_synchronization}"

@app.get("/api/times/M")
def test( K : int, N : int, d : int, algorithm : str, algorithm_security : str ):

    res = {}
    for algorithm_synchronization in SYNC_VERSIONS:
        algorithm_version = get_algorithm_version(algorithm_security, algorithm_synchronization)

        times = []
        for M in list_M:
            recording = read_recording_from_parameters(
                M=M,
                K=K,
                N=N,
                d=d,
            )
            times.append( recording.root.get([ algorithm, algorithm_version, "execution-time" ]) )


        res[algorithm_synchronization] = {
            "param_name": "M",
            "param_values": list_M,
            "times": times,
        }
    return res


@app.get("/api/times/K")
def test( M : int, N : int, d : int, algorithm : str, algorithm_security : str ):

    res = {}
    for algorithm_synchronization in SYNC_VERSIONS:
        algorithm_version = get_algorithm_version(algorithm_security, algorithm_synchronization)

        times = []
        for K in list_K:
            recording = read_recording_from_parameters(
                M=M,
                K=K,
                N=N,
                d=d,
            )
            times.append( recording.root.get([ algorithm, algorithm_version, "execution-time" ]) )


        res[algorithm_synchronization] = {
            "param_name": "K",
            "param_values": list_K,
            "times": times,
        }
    return res


@app.get("/api/times/d")
def test( M : int, N : int, K : int, algorithm : str, algorithm_security : str ):

    res = {}
    for algorithm_synchronization in SYNC_VERSIONS:
        algorithm_version = get_algorithm_version(algorithm_security, algorithm_synchronization)

        times = []
        for d in list_d:
            recording = read_recording_from_parameters(
                M=M,
                K=K,
                N=N,
                d=d,
            )
            #raise Exception(recording.root.tree_of_keys())
            #raise Exception(recording.filename + " " + str(recording.root.keys()))
            assert algorithm in recording.root.keys(), "File " + recording.filename + f" does not contains {algorithm} entry, found entries: " + str(recording.root.keys())
            assert "plaintext-version.no-sync" in recording.root.get(["linucb"]).keys()
            times.append( recording.root.get([ algorithm, algorithm_version, "execution-time" ]) )


        res[algorithm_synchronization] = {
            "param_name": "d",
            "param_values": list_d,
            "times": times,
        }
    return res


@app.get("/api/times/N")
def test( M : int, d : int, K : int, algorithm : str, algorithm_security : str ):

    res = {}
    for algorithm_synchronization in SYNC_VERSIONS:
        algorithm_version = get_algorithm_version(algorithm_security, algorithm_synchronization)

        times = []
        for N in list_N:
            recording = read_recording_from_parameters(
                M=M,
                K=K,
                N=N,
                d=d,
            )
            times.append( recording.root.get([ algorithm, algorithm_version, "execution-time" ]) )


        res[algorithm_synchronization] = {
            "param_name": "N",
            "param_values": list_N,
            "times": times,
        }
    return res




@app.get("/api/theta-mse/sync")
def times( M : int, N : int, K : int, d : int, algorithm : str, algorithm_security : str ):
    """
    Description: Return the time at each time step.
    """

    recording = read_recording_from_parameters(
        M=M,
        K=K,
        N=N,
        d=d,
    )

    return recording.get_theta_mse_by_sync(
        algorithm=algorithm,
        algorithm_security=algorithm_security,
    )


@app.get("/api/component-execution-time/security")
def times( M : int, N : int, K : int, d : int, algorithm : str, algorithm_synchronization : str ):
    """
    Description: Return the time at each time step.
    """
    recording = read_recording_from_parameters(
        M=M,
        K=K,
        N=N,
        d=d,
    )

    return recording.get_component_execution_time_by_security(
        algorithm=algorithm,
        algorithm_sync=algorithm_synchronization,
    )


@app.get("/api/component-execution-time/synchronization")
def times( M : int, N : int, K : int, d : int, algorithm : str, algorithm_security ):
    """
    Description: Return the time at each time step.
    """
    recording = read_recording_from_parameters(
        M=M,
        K=K,
        N=N,
        d=d,
    )

    return recording.get_component_time_by_synchronization(
        algorithm=algorithm,
        algorithm_security=algorithm_security
    )

@app.get("/api/turn/theta-mse")
async def home( M : int, N : int, K : int, d : int, algorithm : str, algorithm_security : str, algorithm_synchronization : str ):
    """
    URL: /turn/theta-mse
    Description: Return the Mean Squared Error at each time step.
    """

    recording = read_recording_from_parameters(
        M=M,
        K=K,
        N=N,
        d=d,
    )
    return recording.get_theta_mse_by_turn( algorithm, algorithm_security, algorithm_synchronization )

















