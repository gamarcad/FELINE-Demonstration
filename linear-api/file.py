from os.path import exists, isfile
from os import mkdir, read
from pathlib import Path
import os
from posixpath import abspath
import json

class IOFileWrapper:
    """Recording object allows to store easily data on file without checking if the file exists or not."""
    def __init__(self, filename) -> None:
        self.absolute_path = os.path.abspath(filename)
        self.dirname = os.path.dirname(self.absolute_path)
        self.filename = filename
    
    def write(self, data) -> None:
        path = Path(self.absolute_path)
        if path.exists() and not path.is_file(): 
            raise Exception("Can only write on object which is a file")
        if not path.exists():
            parent_dir = Path(self.dirname)
            parent_dir.mkdir(parents=True, exist_ok=True)

        with open(self.absolute_path, 'w') as file:
            self._encode_data(data, file)


    def read(self):
        path = Path(self.absolute_path)
        if not path.exists():
            raise Exception(f"File not found: {self.absolute_path}")

        with open(self.absolute_path, 'r') as file:
            return self._decode_data(file)

    def exists(self) -> bool:
        path = Path(self.absolute_path)
        return path.exists()
        

    def _encode_data( self, data, file ): pass
    def _decode_data( self, file ): pass



class JSONFileWrapper(IOFileWrapper):
    """JSON File Wrapper Object"""
    def _encode_data( self, data, file ): file.write(json.dumps(data))
    def _decode_data( self, file ): return json.loads("".join(file.readlines()))


            
