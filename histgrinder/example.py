# collect example code


def transform_function_divide_ROOT(inputs):
    """ This function returns the ratio of two ROOT histograms """
    assert len(inputs) == 1
    cl = inputs[0][1][0].Clone()
    cl.Divide(inputs[0][1][1])
    return [cl]


def transform_function_divide2_ROOT(inputs):
    """ This function returns the ratio of two ROOT histograms """
    cl = inputs[0][1][0].Clone()
    cl.Clear()
    for o in inputs:
        cl2 = o[1][0].Clone()
        cl2.Divide(o[1][1])
        cl.Add(cl2)
    return [cl]


def transform_function_rms_ROOT(inputs):
    """ This function returns the ratio of two ROOT histograms """
    import ROOT
    rv = ROOT.TH1F('RMS', 'RMS of gaussians', 40, 0, 2)
    plots = [_[1][0] for _ in inputs] # all plots passed as first element of list
    for plot in plots:
        rv.Fill(plot.GetRMS())
    return [plot]