# collect example code


def transform_function_test_ROOT(inputs, parameters, regex_matches):
    """ This function returns the ratio of two ROOT histograms """
    print(f"Processing {inputs} {parameters} {regex_matches}")
    cl = inputs[0].Clone()
    cl.Divide(inputs[1])
    return [cl]
