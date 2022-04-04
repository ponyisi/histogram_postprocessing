from subprocess import CalledProcessError
import pytest


def content_verify(newfile=False):
    # ROOT should already have been checked to exist
    import ROOT
    # verify contents
    f = ROOT.TFile.Open("new.root" if newfile else "example.root")
    d = f.Get('prefix')
    # did we create new histograms?
    assert len(d.GetListOfKeys()) == (41 if newfile else 42)
    # correct size?
    assert f.Get("prefix/gauRMS").GetEntries() == 100
    return True


def returncppstr(inputs):
    import cppyy
    return [cppyy.gbl.std.string('abc')]


def test_run_stream():
    pytest.importorskip("ROOT")

    import subprocess
    chk = subprocess.run("python -m histgrinder.make_sample_file",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()
    chk = subprocess.run("python -m histgrinder.engine example.root example.root "
                         "-c tests/test_functional.yaml --prefix prefix",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()

    return content_verify()


def test_run_newfile():
    pytest.importorskip("ROOT")

    import subprocess
    import os.path
    chk = subprocess.run("python -m histgrinder.make_sample_file",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()
    if os.path.exists('new.root'):
        os.remove('new.root')
    chk = subprocess.run("python -m histgrinder.engine example.root new.root -c tests/test_functional.yaml --prefix prefix",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()

    return content_verify(newfile=True)


def test_run_noprefix():
    pytest.importorskip("ROOT")

    import subprocess
    chk = subprocess.run("python -m histgrinder.make_sample_file",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()
    chk = subprocess.run("python -m histgrinder.engine example.root example.root -c tests/test_functional_noprefix.yaml",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()

    return content_verify()


def test_run_absprefix():
    pytest.importorskip("ROOT")

    import subprocess
    import os.path
    chk = subprocess.run("python -m histgrinder.make_sample_file",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()
    if os.path.exists('new.root'):
        os.remove('new.root')
    chk = subprocess.run("python -m histgrinder.engine example.root new.root "
                         "-c tests/test_functional.yaml --prefix /prefix",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()

    return content_verify(newfile=True)


def test_run_defer():
    pytest.importorskip("ROOT")

    import subprocess
    chk = subprocess.run("python -m histgrinder.make_sample_file",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()
    chk = subprocess.run("python -m histgrinder.engine example.root example.root "
                         "-c tests/test_functional.yaml --prefix prefix --defer",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()

    return content_verify()


def test_run_delaywrite():
    pytest.importorskip("ROOT")

    import subprocess
    chk = subprocess.run("python -m histgrinder.make_sample_file",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()
    chk = subprocess.run("python -m histgrinder.engine example.root example.root "
                         "-c tests/test_functional.yaml --prefix prefix --delaywrite",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()

    return content_verify()


def test_run_badpattern():
    pytest.importorskip("ROOT")

    import subprocess
    chk = subprocess.run("python -m histgrinder.make_sample_file",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()
    chk = subprocess.run("python -m histgrinder.engine example.root example.root "
                         "-c tests/test_badpattern.yaml --prefix prefix",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    assert b'ValueError: Pattern specification problem: all named groups must be given in the first pattern' in chk.stdout
    with pytest.raises(subprocess.CalledProcessError):
        chk.check_returncode()


def test_run_badfunction():
    pytest.importorskip("ROOT")

    import subprocess
    chk = subprocess.run("python -m histgrinder.make_sample_file",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()
    chk = subprocess.run("python -m histgrinder.engine example.root example.root "
                         "-c tests/test_badfunction.yaml --prefix prefix",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    assert b'ValueError: math.pi does not appear to be callable' in chk.stdout
    with pytest.raises(subprocess.CalledProcessError):
        chk.check_returncode()


def test_run_noinput():
    pytest.importorskip("ROOT")

    import subprocess
    chk = subprocess.run("python -m histgrinder.engine missing.root missing.root "
                         "-c tests/test_functional.yaml --prefix prefix",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    assert b'Failed to open file missing.root' in chk.stdout
    with pytest.raises(subprocess.CalledProcessError):
        chk.check_returncode()


def test_run_bad_prefix():
    pytest.importorskip("ROOT")

    import subprocess
    chk = subprocess.run("python -m histgrinder.engine example.root example.root "
                         "-c tests/test_functional.yaml --prefix doesNotExist",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    assert b'Access to invalid directory' in chk.stdout
    chk.check_returncode()


def test_run_badtype():
    pytest.importorskip("ROOT")

    import subprocess
    chk = subprocess.run("python -m histgrinder.make_sample_file",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()
    chk = subprocess.run("python -m histgrinder.engine example.root example.root -c tests/test_badtype.yaml --prefix prefix",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()
    assert b'ERROR | ROOT output: unsupported object type string' in chk.stdout


def test_run_badreturn():
    pytest.importorskip("ROOT")

    import subprocess
    chk = subprocess.run("python -m histgrinder.make_sample_file",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()
    chk = subprocess.run("python -m histgrinder.engine example.root example.root -c tests/test_badreturn.yaml --prefix prefix",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    assert b'Function histgrinder.example.nop gave 0 return values but the YAML configuration specifies 1' in chk.stdout
    with pytest.raises(CalledProcessError):
        chk.check_returncode()


def test_run_fullmatch():
    ROOT = pytest.importorskip("ROOT")

    import subprocess
    chk = subprocess.run("python -m histgrinder.make_sample_file",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()
    chk = subprocess.run("python -m histgrinder.engine example.root new.root "
                         "-c tests/test_fullmatch.yaml --prefix prefix",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()

    # verify output
    f = ROOT.TFile.Open("new.root")
    d = f.Get('prefix')
    assert d
    # correct size? Should only be 10!
    assert f.Get("prefix/gauRMS").GetEntries() == 10
    # correct mean? If we're combining the wrong values, mean will be wrong!
    assert pytest.approx(f.Get("prefix/gauRMS").GetMean(), 1e-8) == 0.9992461958826633
    return True


def test_run_bad_variableoutput():
    pytest.importorskip("ROOT")
    import tempfile

    import subprocess
    chk = subprocess.run("python -m histgrinder.make_sample_file",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()

    # Test that we get the correct type of return value from function
    with tempfile.NamedTemporaryFile() as configfile:
        configfile.write(
            rb"""---
Input: [ 'gaussians/gaus_(?P<id0>[23])(?P<id>\d)', 'gaussians/gaus_5(?P<id>\d)' ]
OutputDOF: [ 'id0', 'id' ]
VariableOutput: True
Function: histgrinder.example.transform_function_divide_ROOT
Description: Testing
            """
        )
        configfile.flush()
        chk = subprocess.run(f"python -m histgrinder.engine example.root example.root -c {configfile.name} --prefix prefix",
                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(chk.stdout)
        assert b'Function histgrinder.example.transform_function_divide_ROOT gave a return value which is not a Mapping but VariableOutput functions must do so.' in chk.stdout
        with pytest.raises(CalledProcessError):
            chk.check_returncode()

    # Test that we have the correct kind of keys: here, return an integer
    with tempfile.NamedTemporaryFile() as configfile:
        configfile.write(
            rb"""---
Input: [ 'gaussians/gaus_(?P<id0>\d)(?P<id>\d)', 'gaussians/gaus_(?P<id0>\d)(?P<id>\d)' ]
OutputDOF: [ 'id0' ]
VariableOutput: True
Function: histgrinder.example.transform_function_divide2_ROOT_naming
Parameters: { pattern: 57 }
Description: Testing
            """
        )
        configfile.flush()
        chk = subprocess.run(f"python -m histgrinder.engine example.root example.root -c {configfile.name} --prefix prefix",
                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(chk.stdout)
        assert b'Function histgrinder.example.transform_function_divide2_ROOT_naming gave a return value Mapping where at least one of the keys is not a string.' in chk.stdout
        with pytest.raises(CalledProcessError):
            chk.check_returncode()
