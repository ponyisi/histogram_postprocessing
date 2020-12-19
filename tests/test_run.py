import pytest


def test_run():
    ROOT = pytest.importorskip("ROOT")

    import subprocess
    chk = subprocess.run("python -m histgrinder.make_sample_file",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()
    chk = subprocess.run("wget https://raw.githubusercontent.com/ponyisi/histogram_postprocessing/master/resources/example.yaml -O example.yaml",  # noqa: E501
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()
    chk = subprocess.run("python -m histgrinder.engine example.root example.root -c example.yaml --prefix prefix",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()

    # verify contents
    f = ROOT.TFile.Open("example.root")
    d = f.Get("prefix")
    # did we create new histograms?
    assert len(d.GetListOfKeys()) == 31
    # correct size?
    assert f.Get("prefix/gauRMS").GetEntries() == 100
    return True
