# cms-l1t-analysis

Software package to analyse L1TNtuples

Latest stable version: [version 0.5.1](https://github.com/cms-l1t-offline/cms-l1t-analysis/releases/tag/v0.5.1)

[![Build Status](https://travis-ci.org/cms-l1t-offline/cms-l1t-analysis.svg?branch=master)](https://travis-ci.org/cms-l1t-offline/cms-l1t-analysis) [![DOI](https://zenodo.org/badge/80877637.svg)](https://zenodo.org/badge/latestdoi/80877637) [![Code Health](https://landscape.io/github/cms-l1t-offline/cms-l1t-analysis/master/landscape.svg?style=flat)](https://landscape.io/github/cms-l1t-offline/cms-l1t-analysis/master) [![docs](https://readthedocs.org/projects/cms-l1t-analysis/badge/?version=latest)](http://cms-l1t-analysis.readthedocs.io/en/latest/)

## Run CMS L1T analysis

### Analysis using Singularity

If you have access to Singularity with unprivileged user namespaces (e.g. on LXPLUS), you can run

```bash
ssh <you cern user name>@lxplus.cern.ch
mkdir -p cmsl1t_output

/cvmfs/oasis.opensciencegrid.org/mis/singularity/bin/singularity exec --contain --ipc --pid \
--bind $PWD \
--bind /cvmfs \
--bind $PWD/cmsl1t_output:/opt/cms-l1t-analysis/output  \
/cvmfs/singularity.opensciencegrid.org/cmsl1tanalysis/cmsl1t:0.5.1_root_v6-18-04 bash

# inside the container
cd /opt/cms-l1t-analysis
# you can now run your configs
## to test you can run the demo:
cmsl1t -c config/demo.yaml

# if you need remote access (e.g. grid storage or compute) you will need to also
source /cvmfs/grid.cern.ch/umd-c7ui-latest/etc/profile.d/setup-c7-ui-example.sh
voms-proxy-init -voms cms
```

All results will be put into the `cmsl1t_output` folder and will be available outside the container.

## Development instructions

 1. Read [CONTRIBUTING.md](https://github.com/cms-l1t-offline/cms-l1t-analysis/blob/master/CONTRIBUTING.md)
 2. Follow the instructions below

### On CentOS 7 with CVMFS available

This includes nodes lxplus.cern.ch & private clusters

```bash
git clone https://github.com/<your github user name>/cms-l1t-analysis.git
cd cms-l1t-analysis
git remote add upstream https://github.com/cms-l1t-offline/cms-l1t-analysis.git
git pull --rebase upstream master
source setup.sh
# you will need your grid cert
voms-proxy-init --voms cms
make setup
```

### On OS X/other Linux/Windows

Check the [HEP-DEV-DOCS](https://kreczko.github.io/hep-dev-docs/) for instructions specific to your OS.
You will need to install Docker and CVMFS.

Next, get the code:

```bash
git clone https://github.com/<your github user name>/cms-l1t-analysis.git
cd cms-l1t-analysis
git remote add upstream https://github.com/cms-l1t-offline/cms-l1t-analysis.git

docker run -ti --rm \
-v /cvmfs:/cvmfs:ro \
-v $PWD:/opt/cms-l1t-analysis \
cmsl1tanalysis/cmsl1t-dev:v6-18-04 bash
# inside the container
cd /opt/cms-l1t-analysis
make setup-external
```

### Development using Singularity

If you have access to Singularity with unprivileged user namespaces (e.g. on LXPLUS), you can run

```bash
git clone https://github.com/<your github user name>/cms-l1t-analysis.git
cd cms-l1t-analysis
git remote add upstream https://github.com/cms-l1t-offline/cms-l1t-analysis.git

/cvmfs/oasis.opensciencegrid.org/mis/singularity/bin/singularity exec --contain --ipc --pid \
--bind /cvmfs \
--bind $PWD:/opt/cms-l1t-analysis  \
/cvmfs/singularity.opensciencegrid.org/cmsl1tanalysis/cmsl1t-dev:v6-18-04 bash

# inside the container
cd /opt/cms-l1t-analysis
make setup-external
```

### running tests

Tests can be run either on a CentOS 7 machine or in the Docker/Singularity container:

```bash
make test
# if a grid proxy is provided (e.g. via voms-proxy-init --voms cms)
# you can also run tests that require grid access:
make test-all
```

### running benchmark

```bash
# install python requirements
pip install -r requirements.txt --user
make benchmark
```

### Generating documentation (locally)

Documentation is automatically updated on [read the docs](http://cms-l1t-analysis.readthedocs.io/en/latest/)
whenever a the master branch is updated. If you want to test documentation locally execute

```bash
# HTML version
make docs-html # produces output in docs/_build/html
make docs-latex # produces output in docs/_build/latex
# you might need to
# export PATH:/cvmfs/sft.cern.ch/lcg/external/texlive/2014/bin/x86_64-linux:$PATH
# for docs-latex
```

#### Prerequisites

```bash
gpg --keyserver hkp://keys.gnupg.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3
\curl -sSL https://get.rvm.io | bash -s stable --ruby
source ~/.rvm/scripts/rvmsource ~/.rvm/scripts/rvm
gem install github_changelog_generator
```

### Implementing and running an analysis script

"Analyzers" are the parts of the code that receive events from the input tuples, extracts the relevant data and puts this into the histograms.

You can see an example of an analyzer at: `cmsl1t/analyzers/demo_analyzer.py`.  
To implement your own analyzer, all you need to do is make a new class in a file under `cmsl1t/analyzers/` which inherits from `cmsl1t.analyzers.BaseAnalyzer.BaseAnalyzer`.  You then need to implement two or three methods: `prepare_for_event`, ` fill_histograms`, `write_histograms`, and `make_plots`.  See the BaseAnalyzer class and the demo_analyzer for examples and documentation of these methods.

Once you have implemented an analyzer and written a simple configuration for it, you can run it with `cmsl1t` command:

```bash
cmsl1t -c config/demo.yaml -n 1000
```

Get help on the command line options by doing:

```bash
cmsl1t --help
```

### Testing HTCondor submission

For HTCondor we have an all-in-one Docker container. From the code repo:

```bash
docker-compose up -d
docker exec -ti cmsl1tanalysis_cmsl1t_1 cdw
# do your tests

# logout once done

# shut down the container(s)
docker-compose down
```

**NOTE**: If you are on Linux you have to install `docker-compose` by hand:

```bash
sudo curl -L https://github.com/docker/compose/releases/download/1.15.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

to update you have to `sudo rm -f /usr/local/bin/docker-compose` first.


To build the docker container: `docker-compose build` or `docker build -t kreczko/cms-l1t-analysis -f docker/Dockerfile .`.

## Releases

### Make a new release

Since the changelog generator queries the repository you will need to give it
a github authentication token to bypass the limits for unauthenticated access.
You can create such tokens under https://github.com/settings/tokens .

```bash
export CHANGELOG_GITHUB_TOKEN=<from https://github.com/settings/tokens>
export RELEASE=<release version> #e.g. 0.3.0
git pull --rebase upstream master
make release
```
