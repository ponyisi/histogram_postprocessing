import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="histgrinder",
    version="1.0.0",
    author="Peter Onyisi",
    author_email="ponyisi@utexas.edu",
    description="Generic system to perform streaming transformations on histograms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ponyisi/histogram_postprocessing",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires='>=3.6',
    install_requires=['PyYAML>=5'],
    scripts=['bin/histgrinder']
)
