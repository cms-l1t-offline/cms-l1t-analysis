# cms-l1t-analysis
Software package to analyse L1TNtuples

## Quick-Start Guide for lxplus
 1. Read the README etc if you want to dive deeper!
 2. To get cracking, follow the instructions below:

### On Scientific Linux 6 with CVMFS available, e.g. lxplus, Soolin etc
This includes nodes lxplus.cern.ch & private clusters

For now let's use this repository, you can fork your own of course!
```bash
git clone -b weekly-checks https://github.com/professor-calculus/cms-l1t-analysis.git
cd cms-l1t-analysis
source bin/env.sh
# you might need your grid cert -- but you shouldn't need it on lxplus with NTuples on EOS
voms-proxy-init --voms cms
make setup
```

make setup should work, but in the case that it throws Error 54 ignore it for now. This just means it cannot find
the test NTuples, but everything else is compiled ok and ready to rock 'n' roll.

### running tests
Tests can be run either on an SL 6 machine or in the Vagrant box:
```bash
make test
# if a grid proxy is provided (e.g. via voms-proxy-init --voms cms)
# you can also run tests that require grid access:
make test-all
```

This should fail if make setup threw Error 54.


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

### Running the weekly checks:

For the weekly checks of jets & sums efficiencies, 2D plots etc, we have an analyzer:

Currently this is 'cmsl1t/analyzers/offline_met_analyzer.py' but in the future it will likely get rolled into weekly_analyzer.py.

To run this, we want the config file 'configs/offline_met_studies.yaml'.

Lines in the yaml give the paths for the NTuples, starting with 'root://' and ending with '/L1NTuple_*.root' -- You should edit these to point to the NTuples you're running on.

Further down the yaml file you can specify relative/absolute paths for the output.

Once you're ready, run as so:

```bash
cmsl1t -c config/offline_met_studies.yaml -n <no_of_entries>
```

Or, for large running you can run on lxbatch with the NTuple list broken up into many jobs. Files per job specifiable with -f <number>. Try to keep max ~1000 jobs else combining later is a nightmare.

Also more than about 20 files per job will lead to some going over the walltime... Edit bin/cmsl1t_dirty_batch to change queue from 1nh to something else if this happens a lot.

For small runs I reccommend changing queue to 8nm and running ~4-6 files per job.

Once this submits the jobs it will tell you how to combine them together later :-)

```bash
cmsl1t_dirty_batch -c config/offline_met_studies.yaml -f <ntuple_root_files_per_job>
```
