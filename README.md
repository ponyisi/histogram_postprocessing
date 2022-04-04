# histgrinder
Generic system to perform streaming transformations on histograms

Features:
* core does not depend on any histogram library or input/output format; plugins can be written (and these need not live in this package). Probably most useful if histograms live in a hierarchical namespace but this is not necessary. Example implementation to read/write ROOT files provided.
* intended for streaming, e.g. for online environments where histograms are updated asynchronously.
* pattern matching makes it easy to apply the same transformation to multiple histograms
* no code needed to configure

This is still very much early-release software, you can test it as follows (e.g. should work on lxplus, if you have a CERN account):
* set up ROOT and Python (>=3.7) in a way that you like. For ATLAS people you can set up a master nightly. (The code may run on Python 3.6 but we no longer test it there.)
* install (not needed if you are on ATLAS and using master,2020-10-20T2101 or later): `python3 -m pip install -U --user histgrinder==0.1.5`
* prepare a sample ROOT file: `python3 -m histgrinder.make_sample_file`
* download an example YAML configuration from https://raw.githubusercontent.com/ponyisi/histogram_postprocessing/master/resources/example.yaml 
* run. The following will postprocess `example.root`, created above, according to the `example.yaml` configuration, ignoring the top-level path "prefix", then add the outputs to `example.root`: 

`python3 -m histgrinder.engine example.root example.root -c example.yaml --prefix prefix`
* the transformation above will perform a number of operations on the histograms of the input file. For example, 20 different histogram divisions are configured with the first config block.

Command line arguments:
| Argument | Description |
|--|--|
| `-c`, `--configfile CONFIGFILE [CONFIGFILE ...]` | one or more YAML configuration file(s) |
| `--inmodule` | Python class which implements an input module (default: `histgrinder.io.root.ROOTInputModule`) |
| `--outmodule` | Python class which implements an output module (default: `histgrinder.io.root.ROOTOutputModule`) |
| `--prefix` | Path prefix to ignore in histogram locations in input (will also be prepended to output locations) |
| `--loglevel` | Set the logging level (choices: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`; default: `INFO`) |
| `--defer` |  If specified, defer processing of histograms until all input histograms are read. Major speedups possible if some transformations take a lot of histograms as input. Not for streaming-type jobs. |
| `--delaywrite` | If specified, write histograms at once at end of job. Can speed up tasks if I/O is a bottleneck. Not for streaming-type jobs. |

This work was supported by the US Department of Energy, Office of Science, Office of High Energy Physics, under Award Number DE-SC0007890.
