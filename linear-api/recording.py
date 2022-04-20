from typing import Any, Iterable, List
from pipe import Pipe

from api_model import Configuration
from data import DataWrapper
from file import JSONFileWrapper
from execution_config import ExecutionConfiguration
from copy import deepcopy

# we will annote each output produced by the recording object with a recording version
SYNC_VERSIONS = [
    "no-sync",
    "four-steps",
    "two-steps",
    "each-step"
]

SEC_VERSIONS = [
    "plaintext-version",
    "masked-version",
]

RECORDER_VERSION = "2"
RECORDER_VERSION_KEY = "recorder-version"
RECORDER_DATA_KEY = "recording-data"

# Context Recording
NB_ITERATION_KEY = "nb-iteration"
CONFIG_KEY = "config"

# Execution keys 
ALGORITHM_KEYS = "algorithm"
ALGORITHM_VERSION = "algorithm-version"
SEED_KEY = "seed"
REWARD_SEED_KEY = "reward-seed"
DATA_KEY = "data"

# Description keys
ITERATION_KEY = "iteration"
EXECUTION_TIME_KEY = "execution-time"
EXECUTION_TIME_SERIE_KEY = "execution-time-serie"
REWARDS_KEY = "rewards"
ENTITIES_KEY = "entities"
TURN_BY_TURN_KEY = "turn-by-turn"
THETA_MSE_KEY = "theta-mse"


class RecursiveMap:
    def __init__(self, root={}) -> None:
        self.root = root

    def __setitem__(self, keys, value):
        self.put(keys, value)

    def __getitem__(self, keys):
        return self.get(keys)

    def __str__(self):
        return str(self.root)

    def keys(self):
        return self.root.keys()

    def values(self):
        return self.root.values()

    def items(self):
        for key, value in self.root.items():
            if type(value) == dict:
                yield (key, RecursiveMap(root=value))
            else:
                yield (key, value)

    def __dict__(self):
        return self.root.__dict__

    def __iter__(self):
        if type(self.root) == dict:
            return iter([
                (key, RecursiveMap(root=self.root[key]))
                for key in self.root.keys()
            ])
        else:
            return self.root

    def tree_of_keys(self):
        def internal( node, depth ):
            if type(node) == dict:
                res = ""
                for key, value in node.items():
                    res = res + "\n" +( "--" * depth ) + str(key)  + internal(value, depth + 1)
                return res
            else:
                return " -> "  + str(type(node))
        return internal(self.root, 0)

    def put(self, keys: Iterable, value: Any):
        """Puts a new value under the (possible multiple) keys"""
        current_node = self.root
        for key in keys[:-1]:
            assert type(current_node) == dict
            if key not in current_node:
                current_node[key] = {}
            current_node = current_node[key]
        assert type(current_node) == dict, type(current_node)
        current_node[keys[-1]] = value

    def get(self, keys: Iterable, default=None):
        """Returns the value stored under the (possible multiple) keys"""
        current_node = self.root
        valid_keys_found = []
        for key in keys:
            if key not in current_node:
                if default:
                    return default
                else:
                    raise Exception(f"Key {'/'.join(keys)} not in the map: failure at {valid_keys_found} on {current_node.keys()}")
            valid_keys_found.append(key)
            current_node = current_node[key]


        # this map can return either a leaf or a sub graph
        if type(current_node) == dict:
            return RecursiveMap(root=current_node)
        else:
            return current_node

    def has(self, keys: Iterable) -> bool:
        """Returns True if the (possible multiple) key is contained in the map."""
        current_node = self.root
        for key in keys:
            if key not in current_node:
                return False
            current_node = current_node[key]

        return True

    def export(self):
        return self.root



@Pipe
def mean( values ):
    return sum(values) / len(values)


def merge_lists( list_of_list ):
    if list_of_list == []: return []

    # ensures that all lists of the same length
    first_list_length = len(list_of_list[0])
    for list in list_of_list:
        if len(list) != first_list_length:
            raise Exception("All list does not have the same length")
    # computes the minimum
    return [
        [ list[index] for list in list_of_list ] | mean
        for index in range(first_list_length)
    ]

def merge_recursive_maps( list_maps : List[RecursiveMap], merge_strategy = "uniq" ):
    def internal( keys, res : RecursiveMap ):
        for key, item in list_maps[0][keys].items():

            if type(item) == RecursiveMap:
                internal( keys + [key], res )
            elif type(item) == list:
                res[ keys + [key] ] = merge_lists([ map[keys + [key]] for map in list_maps ])
            elif type(item) == int or type(item) == float:
                res[ keys + [key] ] = [ map[keys + [key]] for map in list_maps ] | mean
            else:
                if merge_strategy == "join":
                    res[keys + [key]] = [map[keys + [key]] for map in list_maps]
                elif merge_strategy == "uniq":
                    values = [map[keys + [key]] for map in list_maps]
                    if len(set(values)) == 1:
                        res[ keys + [key] ] = values[0]
                    else:
                        raise Exception(f"Two different values under the same key {keys + [key]}: {values}")

                elif merge_strategy == "fault":
                    raise Exception("Keys " + str(keys + [key]) + " cannot be merge: type " + str(type(item)))
    res = RecursiveMap(root={})
    internal( [], res )
    return res


class Recording:
    """Recording object"""

    @staticmethod
    def from_file(filename: str):
        """Creates a new Recording object from a filename, or create a new one if file does not exist."""
        file = JSONFileWrapper(filename)
        if file.exists():
            data = file.read()

            # Recognized Recording object only if they have the same version number
            version = data[RECORDER_VERSION_KEY]
            if version != RECORDER_VERSION:
                raise Exception(f"Illegal Recording version: only read {RECORDER_VERSION}, not {version}")

            return Recording(
                version=data[RECORDER_VERSION_KEY],
                root=RecursiveMap(root=data),
                filename=filename,
            )
        else:
            return Recording.new(filename)

    @staticmethod
    def new(filename=None):
        recording = Recording(
            filename=filename,
            version=RECORDER_VERSION,
            root=RecursiveMap({
                RECORDER_VERSION_KEY: RECORDER_VERSION,
                RECORDER_DATA_KEY: {}
            })
        )
        return recording

    def items(self):
        if RECORDER_DATA_KEY in self.root.keys():
            map = self.root.get([RECORDER_DATA_KEY])
        else:
            map = self.root
        return iter([
            (key, map.get([key]))
            for key in map.keys()
        ])

    def __init__(self, version, root: RecursiveMap, filename=None) -> None:
        self.version = version
        self.filename = filename
        self.root: RecursiveMap = root

    def debug_structure(self):
        return self.root.tree_of_keys()

    def create_sub_recording(self, sub_root_key: Iterable):
        """Creates and returns a new recording object which is a sub-recording of the master recording."""
        keys = [RECORDER_DATA_KEY] + sub_root_key
        if not self.root.has(keys):
            self.root.put(keys=keys, value={})
        return Recording(version=self.version, root=self.root.get(keys))

    def get_parameters_configuration(self):
        list_N = set()
        list_K = set()
        list_M = set()
        list_d = set()

        for filename, recording in self.root.get([RECORDER_DATA_KEY]).items():
            list_N.add(recording[["data", "N"]])
            list_K.add(recording[["data", "K"]])
            list_M.add(recording[["data", "M"]])
            list_d.add(recording[["data", "d"]])

        return { "list_N": sorted(list_N), "list_K": sorted(list_K), "list_M": sorted(list_M), "list_d": sorted(list_d) }

    def get_algorithm_version(self, algorithm_security, algorithm_synchronization):
        return f"{algorithm_security}.{algorithm_synchronization}"

    def get_iterations_from_configuration(self, M, N, K, d, algorithm, algorithm_version):
        for filename, recording in self.root.get([RECORDER_DATA_KEY]).items():
            if recording[["data", "N"]] != N: continue
            if recording[["data", "K"]] != K: continue
            if recording[["data", "d"]] != d: continue
            if recording[["data", "M"]] != M: continue

            return recording[[algorithm, algorithm_version]]
        raise Exception(f"Recording when N={N}, K={K}, M={M}, d={d} not found !")

    def get_merged_iterations(self, M, N, K, d, algorithm, algorithm_version ) -> RecursiveMap:
        iterations = self.get_iterations_from_configuration(
            K=K,
            M=M,
            N=N,
            d=d,
            algorithm=algorithm,
            algorithm_version=algorithm_version
        )

        return merge_recursive_maps(
            [iteration for (_, iteration) in iterations.items()],
            merge_strategy="uniq"
        )

    def get_recoding_from_configuration(self, M, N, K, d, algorithm, algorithm_version, iteration):
        for filename, recording in self.root.get([RECORDER_DATA_KEY]).items():
            if recording[["data", "N"]] != N: continue
            if recording[["data", "K"]] != K: continue
            if recording[["data", "d"]] != d: continue
            if recording[["data", "M"]] != M: continue

            return recording[[algorithm, algorithm_version, iteration]]
        raise Exception("Recording not found !")

    def get_rewards_by_turn(self, algorithm : str, algorithm_security : str, algorithm_synchronization : str ):
        algorithm_version = self.get_algorithm_version( algorithm_security, algorithm_synchronization )
        return [
            sum(data_by_turn.get([ REWARDS_KEY, "details"]))
            for (turn, data_by_turn) in self.root.get([
                algorithm,
                algorithm_version,
                TURN_BY_TURN_KEY
            ]).items()
        ]

    def get_time_by_turn(self, configuration: Configuration):
        turns = []
        times = []

        for (turn, data_by_turn) in self.root.get([configuration.algorithm,configuration.algorithm_version,TURN_BY_TURN_KEY]).items():
            turns.append(turn)
            times.append( data_by_turn.get([EXECUTION_TIME_KEY, "sum"]) )

        return {
            "turns": turns,
            "times": times,
        }




    def get_theta_mse_by_sync(self, algorithm: str, algorithm_security: str):
        res = {}
        for algorithm_synchronization in SYNC_VERSIONS:
            algorithm_version = self.get_algorithm_version(algorithm_security, algorithm_synchronization)
            turns = []
            theta_mse = []

            for (turn, data_by_turn) in self.root.get([ algorithm, algorithm_version, TURN_BY_TURN_KEY]).items():
                turns.append(turn)
                theta_mse.append( data_by_turn.get([THETA_MSE_KEY, "details"]) | mean )

            res[algorithm_synchronization] = {
                "turns": turns,
                "theta_mse": theta_mse
            }
        return res




    def get_possible_K_when(self, N: int, M: int, d: int):
        return sorted([
            recording[[ DATA_KEY, "K" ]]
            for filename, recording in self.root[[ RECORDER_DATA_KEY ]].items()
            if recording[[ DATA_KEY, "N" ]] == N and recording[[ DATA_KEY, "M" ]] == M and recording[[ DATA_KEY, 'd' ]] == d
        ])

    def get_times_while_varying_K(self, N : int, M : int, d : int, algorithm, algorithm_security):
        res = {}
        for algorithm_synchronization in SYNC_VERSIONS:
            algorithm_version = self.get_algorithm_version(algorithm_security, algorithm_synchronization)
            K_values = []
            times = []
            for K in self.get_possible_K_when(N=N, M=M,d=d):
                merged_iterations = self.get_merged_iterations(
                    M=M,
                    K=K,
                    d=d,
                    N=N,
                    algorithm=algorithm,
                    algorithm_version=algorithm_version
                )

                K_values.append(K)
                times.append(merged_iterations[[ EXECUTION_TIME_KEY ]])

            res [algorithm_synchronization] = {
                "param_name": "K",
                "param_values": K_values,
                "times": times,
            }
        return res



    def get_possible_N_when(self, M: int, K: int, d: int):
        return sorted([
            recording[[ DATA_KEY, "N" ]]
            for filename, recording in self.root[[ RECORDER_DATA_KEY ]].items()
            if recording[[ DATA_KEY, "K" ]] == K and recording[[ DATA_KEY, "M" ]] == M and recording[[ DATA_KEY, 'd' ]] == d
        ])

    def get_times_while_varying_N(self, K : int, M : int, d : int, algorithm, algorithm_security):
        res = {}
        for algorithm_synchronization in SYNC_VERSIONS:
            algorithm_version = self.get_algorithm_version(algorithm_security, algorithm_synchronization)
            N_values = []
            times = []
            for N in self.get_possible_N_when(K=K, M=M,d=d):
                merged_iterations = self.get_merged_iterations(
                    M=M,
                    K=K,
                    d=d,
                    N=N,
                    algorithm=algorithm,
                    algorithm_version=algorithm_version
                )

                N_values.append(N)
                times.append(merged_iterations[[ EXECUTION_TIME_KEY ]])

            res[algorithm_synchronization] = {
                "param_name": "N",
                "param_values": N_values,
                "times": times
            }
        return res

    def get_possible_d_when(self, M: int, K: int, N: int):
        return sorted([
            recording[[ DATA_KEY, "d" ]]
            for filename, recording in self.root[[ RECORDER_DATA_KEY ]].items()
            if recording[[ DATA_KEY, "K" ]] == K and recording[[ DATA_KEY, "M" ]] == M and recording[[ DATA_KEY, 'N' ]] == N
        ])

    def get_times_while_varying_d(self, K : int, M : int, N : int, algorithm, algorithm_security):
        res = {}
        for algorithm_synchronization in SYNC_VERSIONS:
            algorithm_version = self.get_algorithm_version(algorithm_security, algorithm_synchronization)
            d_values = []
            times = []
            for d in self.get_possible_d_when(K=K, M=M,N=N):
                merged_iterations = self.get_merged_iterations(
                    M=M,
                    K=K,
                    d=d,
                    N=N,
                    algorithm=algorithm,
                    algorithm_version=algorithm_version
                )

                d_values.append(d)
                times.append(merged_iterations[[ EXECUTION_TIME_KEY ]])

            res[algorithm_synchronization] =  {
                "param_name": "d",
                "param_values": d_values,
                "times": times
            }
        return res

    def get_component_execution_time_by_security(self, algorithm: str, algorithm_sync: str):
        res = {}
        for algorithm_sec in SEC_VERSIONS:
            algorithm_version = self.get_algorithm_version(algorithm_sec, algorithm_sync)
            entities = list(self.root.get([algorithm, algorithm_version, ENTITIES_KEY]).export().keys())
            res[algorithm_sec] = {
                "entities": entities,
                "times": [
                    self.root.get([algorithm, algorithm_version, ENTITIES_KEY, entity, EXECUTION_TIME_KEY])
                    for entity in entities
                ]
            }
        return res

    def get_component_time_by_synchronization(self, algorithm: str, algorithm_security: str):
        res = {}
        for algorithm_synchronization in SYNC_VERSIONS:
            algorithm_version = self.get_algorithm_version(algorithm_security, algorithm_synchronization)
            entities = list(self.root.get([algorithm, algorithm_version, ENTITIES_KEY]).export().keys())
            res[algorithm_synchronization] = {
                "entities": [
                    "Server" if entity == "server" else "DO " + str( int(entity.replace("data-owner-", "")) + 1 )
                    for entity in entities
                ],
                "times": [
                    self.root.get([algorithm, algorithm_version, ENTITIES_KEY, entity, EXECUTION_TIME_KEY])
                    for entity in entities
                ]
            }
        return res

    def get_cumulative_time_by_sync(self, algorithm: str, algorithm_security: str):
        res = {}
        for algorithm_synchronization in SYNC_VERSIONS:
            turns = []
            times = []

            algorithm_version = self.get_algorithm_version( algorithm_security, algorithm_synchronization )
            for (turn, data_by_turn) in self.root.get([algorithm, algorithm_version, TURN_BY_TURN_KEY]).items():
                turns.append(turn)
                times.append(data_by_turn.get([EXECUTION_TIME_KEY, "sum"]))

            res[algorithm_synchronization] = {
                "turns": turns,
                "times": times,
            }
        return res

    def get_theta_mse_by_turn(self, algorithm, algorithm_security, algorithm_synchronization):
        algorithm_version = self.get_algorithm_version( algorithm_security, algorithm_synchronization )
        return [
            sum(data_by_turn.get([THETA_MSE_KEY, "details"]))
            for (turn, data_by_turn) in self.root.get([algorithm, algorithm_version, TURN_BY_TURN_KEY]).items()
        ]

    def add_data_recording(self, data: DataWrapper):
        key = [RECORDER_DATA_KEY, DATA_KEY]
        value = data.__dict__
        self.root.put(
            keys=key,
            value=value
        )

    def add_entity_recording(self, algorithm, algorithm_version, iteration, entity, execution_time, reward=None):
        """Put data from a single entity"""
        key = [algorithm, algorithm_version, f"it-{iteration}", ENTITIES_KEY, entity]
        value = {EXECUTION_TIME_KEY: execution_time}
        if (reward): value[REWARDS_KEY] = reward
        self.root.put(
            keys=key,
            value=value
        )

    def add_turn_by_turn_recording(self, algorithm, algorithm_version, iteration, turn_by_turn_data: RecursiveMap):
        key = [algorithm, algorithm_version, f"it-{iteration}", TURN_BY_TURN_KEY]
        self.root[key] = turn_by_turn_data.export()

    def add_execution_configuration(self, execution_config: ExecutionConfiguration):
        """Put contextual data such as the number of iteration"""
        self.root.put(
            keys=[CONFIG_KEY, NB_ITERATION_KEY],
            value=execution_config.nbIteration
        )

    def add_execution_recording(self, algorithm, algorithm_version, execution_config: ExecutionConfiguration, iteration,
                                execution_time, rewards):
        """Add execution recording which contains information for the execution."""

        self.root.put(
            keys=[algorithm, algorithm_version, f"it-{iteration}"],
            value={
                SEED_KEY: execution_config.seed,
                EXECUTION_TIME_KEY: execution_time,
                REWARDS_KEY: rewards,
            }
        )

    def contains_entry(self, algorithm, algorithm_version, iteration):
        return self.root.has(keys=[algorithm, algorithm_version, f"it-{iteration}"])

    def export(self, filename=None):
        """Exports the recording object in a json file."""
        assert filename is not None or self.filename is not None
        if filename is None: filename = self.filename
        file = JSONFileWrapper(filename)
        file.write(self.root.export())


    def merge_and_export(self, filename=None):
        if filename is None: filename = self.filename
        result = RecursiveMap( root=deepcopy(self.root.export()) )

        # yeild iterations for each algorithm version
        for algorithm_version, algorithm_version_iterations in self.root.get(["linucb"]).items():
            iterations = [
                self.root.get(['linucb', algorithm_version, iteration])
                for iteration in algorithm_version_iterations.keys()
            ]
            merged_iterations = merge_recursive_maps(
                list_maps=iterations,
                merge_strategy='mean'
            )
            result.put([ "linucb", algorithm_version ],  merged_iterations.export() )

        assert filename is not None or self.filename is not None
        if filename is None: filename = self.filename
        file = JSONFileWrapper(filename)
        file.write(result.export())
