from argparse import ArgumentParser
from random import randint
from time import time

from data import DataWrapper, generate_arms_for_one_dataowner
from execution_config import ExecutionConfiguration
from file import JSONFileWrapper
from linucb import LINUCB_ALGORITHM, launch_linucb, linucb_versions
from recording import Recording, RecursiveMap


def generate_random_seed(): return randint(1, 1000)

class ETA:
    def __init__(self, nb_tasks) -> None:
        self.start = time()
        self.nb_tasks = nb_tasks
        self.current_task = 0
        self.last_task_done_time = None
    
    def clock(self):
        self.current_task += 1
        self.last_task_done_time = time()
    
    def eta(self):
        if self.current_task == 0: return "--:--:--"
        elapsed_time = self.last_task_done_time - self.start
        estimated_total_time_sec =  int(self.nb_tasks * elapsed_time / self.current_task)
        estimated_time_to_end_sec = estimated_total_time_sec - int(elapsed_time)
        estimated_time_to_end_min = estimated_time_to_end_sec // 60
        estimated_time_to_end_sec = estimated_time_to_end_sec % 60
        estimated_time_to_end_hou = estimated_time_to_end_min // 60
        estimated_time_to_end_min = estimated_time_to_end_min % 60

        return "{:0>2}:{:0>2}:{:0>2}".format(estimated_time_to_end_hou, estimated_time_to_end_min, estimated_time_to_end_sec)


def logger( level, message, writable = False):
    content = "| " * level + "--- "  + message
    end = "\n" if not writable else "\r"
    print( content + end, end="")
from copy import deepcopy
from multiprocessing import Pool, Lock


import tqdm
def launch_benchmark( args ):
    print(f"Binding recording file from {args.output} [DISABLED]" )
    nbIteration = args.iteration

    # define the version to execution
    ALGORITHMS = [
        LINUCB_ALGORITHM
    ]

    VERSIONS = {
        LINUCB_ALGORITHM: linucb_versions( with_security=not args.without_security )
    }

    # we maintains a mapping between the input and the associated results
    fragment_by_input = RecursiveMap(root={})

    for input in tqdm.tqdm(args.inputs, desc="Input"):
        # define the output location
        output_filename = f"{args.output}/fragments/{input}"

        # read the input file
        input_file = JSONFileWrapper( input )
        fragment_by_input[[input, 'input']] = input_file.read()
        fragment_by_input[[input, 'output']] = output_filename

        input_recording: Recording = Recording.new(filename=output_filename)
        data = DataWrapper.from_file(input)
        for algorithm in tqdm.tqdm(ALGORITHMS,desc="Algorithm"):
            for iteration in tqdm.tqdm(range(nbIteration),desc="Iteration"):
                seed = iteration
                input_recording.add_data_recording(data=data)
                for algorithm_security, algorithm_sync in tqdm.tqdm(VERSIONS[algorithm],desc="Version"):
                    algorithm_version = f"{algorithm_security}.{algorithm_sync}"
                    # Skipping the execution is already exists in the recording
                    if not input_recording.contains_entry(algorithm, algorithm_version, iteration):
                        # creating the execution configuration
                        execution_config = ExecutionConfiguration(
                            algorithm=algorithm,
                            algorithm_security=algorithm_security,
                            algorithm_sync=algorithm_sync,
                            nbIteration=nbIteration,
                            iteration=iteration,
                            seed=seed
                        )
                        input_recording.add_execution_configuration(execution_config)

                        # launch the execution
                        if algorithm == LINUCB_ALGORITHM:
                            launch_linucb(data, input_recording, execution_config)
                        else:
                            raise Exception(f"Algorithm not found: {algorithm}")

        input_recording.merge_and_export()

    # export the inputs/fragments mapping in a file
    inputs_fragments_file = JSONFileWrapper(f"{args.output}/fragments.json")
    inputs_fragments_file.write( fragment_by_input.export() )



            


import json
def generate_limited_data(args):
    """Generates dataset."""

    delta = 0.001
    R = 0.01
    gamma = 0.01
    output = args.output

    def parse_entry( entry ):
        list_res = [ value for value in range( entry.get("from"), entry.get("to"), entry.get("step", 1)) ]
        default_res = max(list_res)
        return list_res, default_res

    def export( data, K, M, d, N ):
        filename = output.replace("{N}", str(N)).replace("{K}", str(K)).replace("{M}", str(M)).replace("{d}", str(d))
        print(f"[+] Exporting {filename}")
        data.export(filename)

    with open(args.instances) as file:
        data = json.loads("".join(file.readlines()))
        list_K, max_K = parse_entry(  data.get("K") )
        list_d, max_d = parse_entry(  data.get("d") )
        list_M, max_M = parse_entry(  data.get("M") )
        list_N, max_N = parse_entry(  data.get("N") )
        
        # we use the same dataset that we crop depending on the wanted dataset to be generated
        # dataset: K x d array

        theta = DataWrapper.generate_theta( max_d )
        data_owners_arms = [
            generate_arms_for_one_dataowner( max_K, max_d )
            for _ in range(max_M)
        ]
        
        nb_generated_file = 0

        # varying d
        for d in list_d:
            nb_generated_file += 1

            data = DataWrapper( 
                d = d, 
                K = max_K, 
                N = max_N, 
                M = max_M, 
                gamma = gamma, 
                delta = delta, 
                R = R,
                theta = theta[:d],
                X = [ [ arm[:d] for arm in arms   ] for arms in data_owners_arms ]    
            )
            export( data, max_K, max_M, d, max_N )

        # varying K
        for K in list_K:
            nb_generated_file += 1

            data = DataWrapper( 
                d = max_d, 
                K = K, 
                N = max_N, 
                M = max_M, 
                gamma = gamma, 
                delta = delta, 
                R = R,
                theta = theta,
                X = [ arms[:K] for arms in data_owners_arms ]   
            )
            export( data, K, max_M, max_d, max_N )

        # varying N
        for N in list_N:
            nb_generated_file += 1

            data = DataWrapper( 
                d = max_d, 
                K = max_K, 
                N = N, 
                M = max_M, 
                gamma = gamma, 
                delta = delta, 
                R = R,
                theta = theta,
                X = data_owners_arms   
            )
            export( data, max_K, max_M, max_d, N )

        # varying N
        for M in list_M:
            nb_generated_file += 1

            data = DataWrapper( 
                d = max_d, 
                K = max_K, 
                N = max_N, 
                M = M, 
                gamma = gamma, 
                delta = delta, 
                R = R,
                theta = theta,
                X = data_owners_arms
            )
            export( data, max_K, M, max_d, max_N )
        
        print(f"[V] Generation of {nb_generated_file} datasets done")


def generate_exhaustive_data(args):
    """Generates exhaustive dataset."""

    delta = 0.001
    R = 0.01
    gamma = 0.01
    output = args.output

    def parse_entry(entry):
        list_res = [value for value in range(entry.get("from"), entry.get("to") + 1, entry.get("step", 1))]
        default_res = max(list_res)
        return list_res, default_res

    def export(data, K, M, d, N):
        filename = output.replace("{N}", str(N)).replace("{K}", str(K)).replace("{M}", str(M)).replace("{d}", str(d))
        print(f"[+] Exporting {filename}")
        data.export(filename)

    with open(args.instances) as file:
        data = json.loads("".join(file.readlines()))
        list_K, max_K = parse_entry(data.get("K"))
        list_d, max_d = parse_entry(data.get("d"))
        list_M, max_M = parse_entry(data.get("M"))
        list_N, max_N = parse_entry(data.get("N"))

        theta = DataWrapper.generate_theta(max_d)
        data_owners_arms = [
            generate_arms_for_one_dataowner(max_K, max_d)
            for _ in range(max_M)
        ]
        nb_generated_file = 0

        for N in list_N:
            for M in list_M:
                for K in list_K:
                    for d in list_d:
                        nb_generated_file += 1

                        data = DataWrapper(
                            d=d,
                            K=K,
                            N=N,
                            M=M,
                            gamma=gamma,
                            delta=delta,
                            R=R,
                            theta=theta[:d],
                            X=[[arm[:d] for arm in arms][:K] for arms in data_owners_arms[:M]]
                        )
                        export(data, K, M, d, N)

        print(f"[V] Generation of {nb_generated_file} datasets done")

def generate_data(args):
    if args.mode == "full":
        generate_exhaustive_data(args)
    else:
        generate_limited_data(args)

def create_parser():
    """Returns a parser configured with arguments."""
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    bench_parser = subparsers.add_parser("benchmark")
    bench_parser.set_defaults(func=launch_benchmark)
    bench_parser.add_argument("--iteration", required=True, type=int)
    bench_parser.add_argument("--inputs", nargs="+", required=True)
    bench_parser.add_argument("--output", required=True)
    bench_parser.add_argument("--without-security", required=False, action="store_true")
    
    data_parser = subparsers.add_parser("data")
    data_parser.set_defaults(func=generate_data)
    data_parser.add_argument("--mode", choices=["full", "max"], help="Specify the mode to generate data.", default="max", required=True)
    data_parser.add_argument("--instances",required=True, help="CSV file that contains the instances to generate.")
    data_parser.add_argument("--output", required=True, help="Generated filenames (support the replacement \{K\},\{M\},\{N\},\{d\}")
    return parser

def main():
    """Entry point for the benchmark."""
    parser = create_parser()
    args = parser.parse_args()
    args.func(args)

    

if __name__ == "__main__":
    main()