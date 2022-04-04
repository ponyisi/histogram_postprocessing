# Configuration file format
The configuration files are in the YAML format. Each transformer is configured by a separate YAML "document"; each document starts with a line consisting of three dashes:

    ---

The configuration options for each transformer are specified in the format `Key: Value`. A minimal example:

    Input: [ 'some/histogram/input/path' ]
    Output: [ 'some/histogram/output/path' ]
    Function: some.python.function
    Description: A string

A valid configuration must include `Input`, `Function`, `Description`, and either `Output` or `VariableOutput` keys. Optional keys are `OutputDOF` and `Parameters`.

## Description of the configuration keys
* `Description`: a string that serves to identify the transformer.
* `Function`: a string that specifies the fully qualified name of a Python function (i.e. `package.function_name`) that implements the transformation.
* `Input`: a list of strings. The strings specify the paths for the histograms that must exist to trigger the running of the transformer. Every string in the input list is interpreted as a regular expression. If there is more than one string in the list, the matching input histograms will be passed in the corresponding slots. Named groups in the input regular expressions, together with patterns in the output strings, will determine exactly how the transformers are called when there are multiple matching input histograms; see [later](#input-regular-expressionoutput-pattern-interaction) for more information.
* `Output`: a list of strings. The strings specify the storage paths for the histograms output by the transformers. The output strings can contain patterns to be substituted with named groups from the `Input` block; these are surrounded by braces (i.e. `"{pattern}"`). See [later](#input-regular-expressionoutput-pattern-interaction) for more information.
*`Output` cannot be specified at the same time as `VariableOutput`.*
* `VariableOutput`: a boolean (which defaults to `False`, so only needs to be set if `True`). This indicates that the transformer function itself will give the path for the output histograms. Useful if the number of output histograms is not known in advance but only determined at runtime. Patterns like those used for `Output` can be given for the histogram names, and the expected substitutions will be done. *`VariableOutput` cannot be specified at the same time as `Output`.*
* `OutputDOF`: a list of strings, which specify the named regular expression groups that effectively appear in the output of a `VariableOutput` transformer. This allows histgrinder to apply the same pattern matching rules as given [here](#input-regular-expressionoutput-pattern-interaction) without knowing the actual histogram names. *Cannot be specified unless VariableOutput is True.*
* `Parameters`: a dictionary whose keys are strings; the values can be anything. These are passed as keyword arguments to the transformer function and allow very generic functions to be written and specialized for particular transformer instances.

## Input regular expression/output pattern interaction
One of the most powerful features of histgrinder is its pattern matching capability, which allows transformations on multiple sets of histograms to be specified in a concise way. Let's say we have detectors `A`, `B`, and `C`, and histograms for different thresholds `X_hi` and `X_lo`, where `X` is the detector name, created for each (so six histograms in total). We can specify a number of different potential transformations:

* The following collects all six histograms as inputs to a transformer, with one output histogram (like a global summary plot), because no regular expression patterns given for the input are used in the output:

        Input: [ '(?P<detector>A|B|C)_(?P<threshold>hi|lo)' ]
        Output: [ 'summaryPlot' ]

* The following runs the transformer three times, one for each detector, with each call containing the corresponding `_hi` and `_lo` plot for each detector:

        Input: [ '(?P<detector>A|B|C)_(?P<threshold>hi|lo)' ]
        Output: [ 'summaryPlot_{detector}' ]

* The following runs the transformer two times, one for threshold, with each call containing the three plots corresponding to the three detectors:

        Input: [ '(?P<detector>A|B|C)_(?P<threshold>hi|lo)' ]
        Output: [ 'summaryPlot_{threshold}' ]

* The following runs the transformer six times, one for each of the input plots, because both named groups appear as patterns in the output:

        Input: [ '(?P<detector>A|B|C)_(?P<threshold>hi|lo)' ]
        Output: [ 'summaryPlot_{detector}_{threshold}' ]

Patterns will be matched across all the histograms provided in the input. For example, the following will match the detector/threshold plots above with efficiency plots `(A|B|C)_efficiency` appropriate for each detector:

    Input: [ '(?P<detector>A|B|C)_(?P<threshold>hi|lo)', '(?P<detector>A|B|C)_efficiency' ]
    Output: [ 'summaryPlot_{detector}' ]

In this case, the transformer will be called three times; there will be two collections of histograms in the input each time, corresponding to the valid pairings of the threshold plots with the efficiency plots for a specific detector.

All patterns referenced in a transformer must appear in the first `Inputs` specification.

When using `VariableOutput` transformers, the `OutputDOF` parameter can be given to specify the named groups that would otherwise be present in the `Output` specification, in order to drive the internal pattern matching when invoking the transformer. If `OutputDOF` is not specified the behavior will be as in the first case given above (all matching histograms passed at once).

## Input format for transformer functions
The first (and only required) argument for transformer functions (which we'll call `inputs` here) is an object of Python type `List[Tuple[Dict[str, str], List[Any]]]`, i.e. a list of pairs, each pair including a dictionary as the first item and a list of histograms as the second. Definition:
* The top-level list (`inputs`) has a distinct item for every allowed regular expression match set, as determined by the [pattern matching rules](#input-regular-expressionoutput-pattern-interaction). If a named group is getting "flattened" (i.e. there are fewer patterns in the `Output`/`OutputDOF` than named groups in the `Input`) then the `inputs` list will have more than one item. For example, in the last example above:

        Input: [ '(?P<detector>A|B|C)_(?P<threshold>hi|lo)', '(?P<detector>A|B|C)_efficiency' ]
        Output: [ 'summaryPlot_{detector}' ]

    the `inputs` list will have two entries per call (from `hi` and `lo`).

* For each entry of `inputs`, there is a tuple, the first item of which (`inputs[i][0]`) specifies the corresponding values of all named groups, and the second of which (`inputs[i][1]`) is a list of individual histogram objects, of the same length as the `Inputs` specification in the configuration file, with the plots in positions corresponding to the `Inputs`. So in the example above, the first entry of each tuple will be a dictionary like `{'detector': 'A', 'threshold': 'hi'}`, and the second will be a list like `[A_hi, A_efficiency]`.