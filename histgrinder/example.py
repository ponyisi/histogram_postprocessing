# collect example code


def transform_function_divide_ROOT(inputs):
    """ This function returns the ratio of two ROOT histograms """
    # there should only be one match at a time. inputs[0] will describe that match.
    assert len(inputs) == 1  # for testing
    # inputs[0] is a pair of (dict describing the regex matches, list of histograms)
    # so we expect inputs[0][1] to be a pair, should have length 2
    assert len(inputs[0][1]) == 2
    cl = inputs[0][1][0].Clone()
    cl.Divide(inputs[0][1][1])
    return [cl]


def transform_function_divide2_ROOT(inputs):
    """ This function returns the ratio of two ROOT histograms """
    assert len(inputs) == 10
    cl = inputs[0][1][0].Clone()
    cl.Clear()
    for o in inputs:
        cl2 = o[1][0].Clone()
        cl2.Divide(o[1][1])
        cl.Add(cl2)
    return [cl]


def transform_function_divide2_ROOT_naming(inputs, pattern):
    """ This function returns the ratio of two ROOT histograms """
    assert len(inputs) == 10
    cl = inputs[0][1][0].Clone()
    cl.Clear()
    for o in inputs:
        cl2 = o[1][0].Clone()
        cl2.Divide(o[1][1])
        cl.Add(cl2)
    return {pattern: cl}


def transform_function_rms_ROOT(inputs):
    """ This function plots the RMSes of a list of ROOT histograms """
    import ROOT
    rv = ROOT.TH1F('RMS', 'RMS of gaussians', 40, 0, 2)
    plots = [_[1][0] for _ in inputs]  # all plots passed as first element of list
    for plot in plots:
        rv.Fill(plot.GetRMS())
    return [rv]


def nop(inputs):
    """ This function does nothing but may be useful for debugging """
    print(list(inputs))
    return []


def nop_var(inputs):  # pragma: no cover
    """ This function does nothing but may be useful for debugging """
    print(list(inputs))
    return {}
