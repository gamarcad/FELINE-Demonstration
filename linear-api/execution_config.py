class ExecutionConfiguration:
  """
  Execution Configuration contains information that are used to launch an algorithm.
  """
  def __init__(self, algorithm, algorithm_security, algorithm_sync, nbIteration, iteration, seed) -> None:
      self.algorithm = algorithm
      self.algorithm_version = f"{algorithm_security}.{algorithm_sync}"
      self.algorithm_security = algorithm_security
      self.algorithm_sync = algorithm_sync
      self.nbIteration = nbIteration
      self.iteration = iteration
      self.seed = seed