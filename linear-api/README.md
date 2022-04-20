# LinUCB in a Federated Learning context

## Launching the benchmark
To launch the benchmark, you need to follow two steps:
1. Generating datasets.
2. Launch the benchmark program over the previously generated datasets.

These steps are performed by two independent shell scripts that can be launch with this command:
```sh
./generate_data.sh && ./launch_benchmark.sh
```

## Project structure
The project follows the KISS principle where one program do one more thing well:
1. `data.py` called through `main.py` generates the dataset
2. `linucb.py` called through `main.py` performs the benchmark
3. `summarize.py` called through `main.py` performs a summarization of the recording.

## Cleaning the repository
To wipe out all files produced by the benchmarking (including results), execute the following commands:
```sh
rm -R data results
```

## Naive version
The naive version of our protocol rely on Paillier cryptosystem to perform addition of matrixes.

## Troubleshooting
If you got `ModuleNotFound` error, please install the required python packages with the following commands `pip install -r requirements.txt`