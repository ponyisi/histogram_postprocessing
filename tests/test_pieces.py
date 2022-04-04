import pytest


def test_rootio():
    pytest.importorskip("ROOT")

    from histgrinder.io.root import ROOTInputModule
    rim = ROOTInputModule()
    with pytest.raises(ValueError):
        rim.configure({})

    from histgrinder.io.root import ROOTOutputModule
    rom = ROOTOutputModule()
    with pytest.raises(ValueError):
        rom.configure({})

    # this is just for coverage completeness (tests the branch if the ROM.queue is empty on write)
    rom.configure({'target': ''})
    rom.finalize()

    # this is also for coverage completeness (see that we get everything if no selector is set for the input module)
    import subprocess
    chk = subprocess.run("python -m histgrinder.make_sample_file",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()

    rim.configure({'source': 'example.root'})
    inputs = list(rim.iterate(dryrun=True))
    assert len(inputs) == 101


def test_badconfig():
    from histgrinder.config import read_configuration
    c = read_configuration('tests/test_badconfig.yaml')
    assert c == []


def test_read_config_from_filelike_object():
    from histgrinder.config import read_configuration
    c = read_configuration(open('tests/test_functional.yaml'))
    print(repr(c[0]))
    assert (repr(c[0]) == r"""Description: Testing1
Input: ['gaussians/gaus_(?P<id0>[23])(?P<id>\\d)', 'gaussians/gaus_5(?P<id>\\d)']
Output: ['gauDiv_{id0}{id}']
Function: histgrinder.example.transform_function_divide_ROOT, Parameters: {}""")
    assert (repr(c[2]) == r"""Description: Testing3
Input: ['gaussians/gaus_(?P<id0>\\d)(?P<id>\\d)', 'gaussians/gaus_(?P<id0>\\d)(?P<id>\\d)']
VariableOutput: True, OutputDOF: ['id0']
Function: histgrinder.example.transform_function_divide2_ROOT_naming, Parameters: {'pattern': 'gauDiv3_{id0}'}""")


def test_read_nonexistent_config():
    from histgrinder.config import read_configuration
    with pytest.raises(FileNotFoundError):
        read_configuration('tests/missing.yaml')


def test_clash_variableoutput():
    import histgrinder.config
    from histgrinder.config import read_configuration
    import io

    print(histgrinder.config)
    # Can't specify OutputDOF without VariableOutput
    f = io.StringIO(r"""
---
Input: [ 'gaussians/gaus_(?P<id0>\d)(?P<id>\d)', 'gaussians/gaus_(?P<id0>\d)(?P<id>\d)' ]
OutputDOF: [ 'id0' ]
Function: afunction
Description: Test
    """)
    with pytest.raises(ValueError):
        read_configuration(f)

    # Can't specify Output and VariableOutput
    f = io.StringIO(r"""
---
Input: [ 'gaussians/gaus_(?P<id0>\d)(?P<id>\d)', 'gaussians/gaus_(?P<id0>\d)(?P<id>\d)' ]
Output: [ 'gauDiv_{id0}' ]
VariableOutput: True
Function: afunction
Description: Test
    """)
    with pytest.raises(ValueError):
        read_configuration(f)
