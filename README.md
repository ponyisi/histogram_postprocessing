# histgrinder
Generic system to perform streaming transformations on histograms

Features:
* core does not depend on any histogram library or input/output format; plugins can be written (and these need not live in this package). Probably most useful if histograms live in a hierarchical namespace but this is not necessary. Example implementation to read/write ROOT files provided.
* intended for streaming, e.g. for online environments where histograms are updated asynchronously.
* pattern matching makes it easy to apply the same transformation to multiple histograms
* no code needed to configure

This is still very much early-release software, you can test it as follows (e.g. should work on lxplus, if you have a CERN account):
* set up ROOT and Python (>=3.6) in a way that you like. For ATLAS people you can set up a master nightly.
* install (not needed if you are on ATLAS and using master,2020-10-20T2101 or later): `python3 -m pip install -U --user histgrinder==0.1.3`
* prepare a sample ROOT file: `python3 -m histgrinder.make_sample_file`
* download an example YAML configuration from https://raw.githubusercontent.com/ponyisi/histogram_postprocessing/master/resources/example.yaml 
* run. The following will postprocess `example.root`, created above, according to the `example.yaml` configuration, ignoring the top-level path "prefix", then add the outputs to `example.root`: 

`python3 -m histgrinder.engine example.root example.root -c example.yaml --prefix prefix`
* the transformation above will perform a number of operations on the histograms of the input file. For example, 20 different histogram divisions are configured with the first config block.
