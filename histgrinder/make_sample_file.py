if __name__ == '__main__': # pragma: no test
    import ROOT
    import random
    random.seed(42)

    f = ROOT.TFile.Open('example.root', 'RECREATE')
    f.mkdir('prefix/gaussians')
    f.cd('prefix/gaussians')
    for i in range(100):
        h = ROOT.TH1F(f'gaus_{i}', f'Gaussian {i}', 40, -4, 4)
        for j in range(1000):
            h.Fill(random.gauss(0, 1))
        h.Write()
    f.Close()
