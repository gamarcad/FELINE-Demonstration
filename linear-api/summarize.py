# The job of this file is to transform th 

from recording import Recording
from file import IOFileWrapper
from data import DataWrapper
from pipe import Pipe, groupby, map, select, traverse, chain, sort
from argparse import ArgumentParser

class Table:
    def __init__(self) -> None:
        self.headers = set()
        self.required_headers = set()
        self.data = []
    
    def add_headers( self, **headers ):
        for header, required in headers.items():
            self.headers.add(header)
            if required:
                self.required_headers.add(header)
    
    def add_entry( self, **entry ):
        # fails when at least one required header is missing
        for required_header in self.required_headers:
            if required_header not in entry:
                raise Exception(f"Table Error: Required column not in the entry: {required_header}")

        # insert entry
        self.data.append(entry)
        for column_name in entry.keys():
            self.headers.add(column_name)

TABLE_SEP=","
class TableWrapper(IOFileWrapper):
    """Table File Wrapper Object"""
    def _encode_data( self, table : Table, file ): 
        # the first line contains the header
        file.write( TABLE_SEP.join(table.headers | sort) + "\n" )
        # one line contains one entry
        for entry in table.data:
            line = TABLE_SEP.join([
                str(entry[column]) if column in entry else "_"
                for column in table.headers | sort
            ])
            file.write( line + "\n" )

    def _decode_data( self, file ): 
        raise Exception("Not implemented")

@Pipe
def mean( values ): 
    values = list(values)
    return sum(values) / len(values)


@Pipe
def max_pipe( values ): 
    return max(values)

@Pipe
def min_pipe( values ):
    return min(values)


@Pipe
def rewards( dict ):
    return dict | select( lambda it: it.get(['rewards']) )

@Pipe
def debug( data ):
    print(f"##{data}//")
    return data

@Pipe
def exec_time( dict ):
    return dict | select( lambda it: it.get(['execution-time']) )



@Pipe
def exec_time_by_entity( dict ):
    return dict \
        | select( lambda it: it.get(['entities']) ) \
        | select( lambda dict: [(entity, dict.get([entity, "execution-time"])) for entity in dict.keys()]  )\
        | chain\
        | groupby(lambda couple: couple[0])\
        | select( lambda couple: 
            (
                couple[0] + ".time",
                couple[1] | select( lambda c: c[1]) | mean
            )
        )

ENTITY = str
TIME = float
from typing import Mapping
@Pipe
def max_data_owner_time( dict : Mapping[ENTITY, TIME] ):
     return [
        time
        for (entity, time) in dict.items()
        if "data-owner" in entity
     ] | max_pipe

@Pipe
def rewards_by_data_owner( dict : Mapping[ENTITY, TIME] ):
     return dict \
        | select( lambda it: it.get(['entities']) ) \
        | select( lambda dict: [(entity, dict.get([entity, "rewards"])) for entity in dict.keys() if "data-owner" in entity]  )\
        | chain\
        | groupby(lambda couple: couple[0])\
        | select( lambda couple: 
            (
                couple[0] + ".rewards",
                couple[1] | select( lambda c: c[1]) | mean
            )
        )

def summarize_recording( recording : Recording ) -> Table:
    table = Table()
    table.add_headers( N=True, K=True, M=True, d=True )
    for data_filename, data_recording in recording.items():
        data : DataWrapper = DataWrapper.from_file(data_filename, must_exists=True)
        for algorithm_name, algorithm_recording  in data_recording.items():
            # exclude configuration 
            if algorithm_name == 'config': continue
            for algorithm_version, algorithm in algorithm_recording.items():
                iterations = [value for key, value in algorithm.items()]
                mean_rewards = iterations | rewards | mean
                mean_execution_time = iterations | exec_time | mean
                execution_time_by_entity = { entity: execution_time for (entity, execution_time) in iterations | exec_time_by_entity }
                data_owner_rewards =  { entity: execution_time for (entity, execution_time) in iterations | rewards_by_data_owner }
                table.add_entry(
                    N=data.N,
                    K=data.K,
                    M=data.M,
                    d=data.d,
                    algorithm_name=algorithm_name,
                    algorithm_version=algorithm_version,
                    mean_rewards = mean_rewards,
                    mean_execution_time = mean_execution_time,
                    max_execution_time = iterations | exec_time | max_pipe,
                    min_execution_time = iterations | exec_time | min_pipe,
                    max_data_owner_time = execution_time_by_entity | max_data_owner_time,
                    **execution_time_by_entity,
                    **data_owner_rewards
                )

    return table
        

def export_table( table : Table, filename ):
    table_wrapper = TableWrapper( filename )
    table_wrapper.write( table )

    
def create_parser():
    parser = ArgumentParser()
    parser.add_argument("--input", required=True, help="Results input filename")
    parser.add_argument("--output", required=True, help="Summarize output filename")
    return parser
import os
from pathlib import Path
if __name__ == "__main__":

    # parse arguments
    parser = create_parser()
    args = parser.parse_args()
    input = args.input
    output = args.output

    input_path = Path(input)
    if not input_path.exists() or not input_path.is_file():
        print("Input file does not exist or not a file")
        exit(1)
    
    output_path = Path(output)
    if output_path.exists():
        print("Output file exists")
        exit(1)

    # create the output parents directory if missing
    output_absolute = os.path.abspath(output)
    dirname = os.path.dirname(output_absolute)
    Path(dirname).mkdir( parents=True, exist_ok=True )

    # launch the summarization
    recording = Recording.from_file( input )
    table : Table = summarize_recording(recording)
    export_table( table, output )

    if False:
        FILENAME = "results_2021_12_24"
        recording = Recording.from_file( f"results/{FILENAME}.json" )
        table : Table = summarize_recording(recording)
        export_table( table, f"csv/{FILENAME}.csv" )

    