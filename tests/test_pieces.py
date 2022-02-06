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


def test_read_nonexistent_config():
    from histgrinder.config import read_configuration
    with pytest.raises(FileNotFoundError):
        read_configuration('tests/missing.yaml')
