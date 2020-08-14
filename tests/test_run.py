def test_run():
    import subprocess
    chk = subprocess.run("python -m histgrinder.make_sample_file",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()
    chk = subprocess.run("wget https://raw.githubusercontent.com/ponyisi/histogram_postprocessing/master/resources/example.yaml",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()
    chk = subprocess.run("python -m histgrinder.engine example.root example.root -c example.yaml --prefix prefix",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(chk.stdout)
    chk.check_returncode()
    return True
