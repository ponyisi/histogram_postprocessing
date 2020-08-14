# Configuration utilities
from typing import Union, IO, List, Any
import logging

class TransformationConfiguration(object):
    def __init__(self, Input, Output, Function, Description, Parameters={}):
        self.input = Input
        self.output = Output
        self.function = Function
        self.parameters = Parameters
        self.description = Description

    def __repr__(self):
        return (f"Description: {self.description}\nInput: {self.input}\nOutput: {self.output}\n"
                f"Function: {self.function}, Parameters: {self.parameters}")

def read_configuration(f: Union[str, IO]) -> List[TransformationConfiguration]:
    import yaml
    if isinstance(f, str):
        fobj = open(f)
    else:
        fobj = f

    rv = []
    for doc in yaml.safe_load_all(fobj):
        try:
            rv.append(TransformationConfiguration(**doc))
        except TypeError as e:
            log = logging.getLogger(__name__)
            log.error("Unable to understand the following configuration:")
            log.error(doc)
            log.error(f"Error message: {e}")
    return rv

def lookup_name(name: str) -> Any:
    import importlib
    name = name.rsplit('.', 1)
    return getattr(importlib.import_module(name[0]), name[1])

if __name__ == "__main__":
    import sys
    for _ in read_configuration(sys.argv[1]):
        print(_)