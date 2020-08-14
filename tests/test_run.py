def test_run():
    import subprocess
    chk = subprocess.run("python -m histgrinder.make_sample_file", shell=True)
    if chk:
        return False
    chk = subprocess.run("wget https://github.com/ponyisi/histogram_postprocessing/blob/master/resources/example.yaml",
                         shell=True)
    if chk:
        return False
    chk = subprocess.run("python -m histgrinder.engine example.root example.root -c example.yaml --prefix prefix",
                         shell=True)
    return chk == 0
