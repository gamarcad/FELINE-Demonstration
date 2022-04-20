class Configuration:
    def __init__(self, algorithm, algorithm_sec, algorithm_sync, M, N, K, d):
        self.algorithm = algorithm
        self.algorithm_version = f"{algorithm_sec}.{algorithm_sync}"
        self.M = M
        self.N = N
        self.K = K
        self.d = d

    def has_specified_iteration(self): return self.iteration is not None

    @staticmethod
    def from_data( data : dict, iteration_required : bool = False ):
        # ensures that requires parameters are provided
        if 'M' not in data: raise Exception("M not provided")
        if 'N' not in data: raise Exception("N not provided")
        if 'K' not in data: raise Exception("K not provided")
        if 'd' not in data: raise Exception("d not provided")
        if 'algorithm' not in data: raise Exception("Algorithm not provided")
        if 'algorithm-security' not in data: raise Exception("Algorithm security not provided")
        if 'algorithm-synchronization' not in data: raise Exception("Algorithm synchronization not provided")
        if  iteration_required and 'iteration' not in data: raise Exception("Iteration not provided")

        # create the configuration
        return Configuration(
            M = data["M"],
            N = data["N"],
            K = data["K"],
            d = data["d"],
            iteration = data["iteration"] if "iteration" in data else None ,
            algorithm = data["algorithm"],
            algorithm_sec = data["algorithm-security"],
            algorithm_sync = data["algorithm-synchronization"],
        )
