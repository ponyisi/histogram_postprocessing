if __name__ == '__main__':  # pragma: no cover
    import ROOT
    import random
    import array
    random.seed(42)

    f = ROOT.TFile.Open('example.root', 'RECREATE')
    f.mkdir('prefix/gaussians')
    f.cd('prefix/gaussians')
    for i in range(100):
        h = ROOT.TH1F(f'gaus_{i}', f'Gaussian {i}', 40, -4, 4)
        for j in range(1000):
            h.Fill(random.gauss(0, 1))
        h.Write()

    # make a graph
    x = array.array('f', [1])
    y = array.array('f', [1])
    g = ROOT.TGraph(1, x, y)
    g.Write('graph')

    # make a tree
    t = ROOT.TTree('tree', 'tree')
    t.Branch('x', x, 'x/F')
    t.Fill()
    t.Write()
    f.Close()
