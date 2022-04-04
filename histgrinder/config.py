# Configuration utilities
from typing import Union, IO, List, Any, Mapping
import logging


class TransformationConfiguration(object):
    def __init__(self, Input: List[str], Function: str, Description: str, Output: List[str] = [],
                 VariableOutput: bool = False, OutputDOF: List[str] = [], Parameters: Mapping[str, Any] = {}):
        self.input = Input
        self.output = Output
        self.function = Function
        self.parameters = Parameters
        self.description = Description
        self.variable_output = VariableOutput
        self.output_dof = OutputDOF

        # check for conflicting options
        if OutputDOF and not VariableOutput:
            raise ValueError('Cannot specify OutputDOF if not also setting VariableOutput: True.')
        if Output and VariableOutput:
            raise ValueError('Cannot specify Output if VariableOutput == True.')

    def __repr__(self):
        if self.variable_output:
            return (f"Description: {self.description}\nInput: {self.input}\n"
                    f"VariableOutput: True, OutputDOF: {self.output_dof}\n"
                    f"Function: {self.function}, Parameters: {self.parameters}")
        else:
            return (f"Description: {self.description}\nInput: {self.input}\n"
                    f"Output: {self.output}\n"
                    f"Function: {self.function}, Parameters: {self.parameters}")


def read_configuration(f: Union[str, IO]) -> List[TransformationConfiguration]:
    import yaml
    if isinstance(f, str):
        fobj = open(f, 'r')
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
    spname = name.rsplit('.', 1)
    return getattr(importlib.import_module(spname[0]), spname[1])


if __name__ == "__main__":  # pragma: no cover
    import sys
    for _ in read_configuration(sys.argv[1]):
        print(_)
