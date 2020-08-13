# histgrinder
Generic system to perform streaming transformations on histograms

Features:
* core does not depend on any histogram library or input/output format; plugins can be written (and these need not live in this package). Probably most useful if histograms live in a hierarchical namespace but this is not necessary. Example implementation to read/write ROOT files provided.
* intended for streaming, e.g. for online environments where histograms are updated asynchronously.
* pattern matching makes it easy to apply the same transformation to multiple histograms
* no code needed to configure

This is still very much early-release software, you can test it as follows (e.g. should work on lxplus, if you have a CERN account):
* set up ROOT and Python (>=3.6) in a way that you like. For ATLAS people you can set up a master nightly.
* install: `python3 -m pip install --extra-index-url https://test.pypi.org/simple/ -U --user histgrinder`
* prepare a sample ROOT file: `python3 -m histgrinder.make_sample_file`
* download an example YAML configuration from https://raw.githubusercontent.com/ponyisi/histogram_postprocessing/master/resources/example.yaml 
* run. The following will postprocess `example.root`, created above, according to the `example.yaml` configuration, ignoring the top-level path "prefix", then dump the outputs to `example.root`: 

`python3 -m histgrinder.engine example.root example.root -c example.yaml --prefix prefix`
* the transformation above will divide the prefix/gaussians/gaus_2x and prefix/gaussians/gaus_3x histograms by the prefix/gaussians/gaus_5x histogram (matching x between them) and write the output to prefix/gauDiv_2x or prefix/gauDiv_3x. So 20 different histogram divisions are configured with one config block.
