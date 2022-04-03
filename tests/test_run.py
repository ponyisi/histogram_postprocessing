from subprocess import CalledProcessError
import pytest


def content_verify(newfile=False):
    # ROOT should already have been checked to exist
    import ROOT
    # verify contents
    f = ROOT.TFile.Open("new.root" if newfile else "example.root")
    d = f.Get('prefix')
    # did we create new histograms?
    assert len(d.GetListOfKeys()) == (32 if newfile else 33)
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
    # correct size? Should only be 10, not 100!
    assert f.Get("prefix/gauRMS").GetEntries() == 10
    return True
