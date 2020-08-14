def test_run():
    import subprocess
    chk = subprocess.run("python -m histgrinder.make_sample_file")
    if chk: return False
    chk = subprocess.run("wget https://github.com/ponyisi/histogram_postprocessing/blob/master/resources/example.yaml")
    if chk: return False
    chk = subprocess.run("python3 -m histgrinder.engine example.root example.root -c example.yaml --prefix prefix")
    return chk == 0