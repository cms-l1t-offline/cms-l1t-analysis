'''
YAML Config parser for cmsl1t
A config file consists of muliple sections. The ``general`` section describes
the version and name of the config.

.. code-block:: yaml

   general:
     version: 0.0.1
     name: Benchmark


The input section describes the data that is to be processed and might be
changed in the near future. The first
subsection, ``files``, is a list of files that can be either relative paths,
absolute paths or global paths (e.g. xrootd) and can include wildcards.

.. code-block:: yaml

   input:
     files:
       - data/L1Ntuple_*.root

The second subsection, ``sample`` is used to describe the data: The name of the
dataset, the title and the run number. The name is likely used in file and histogram names,
while the title is meant to be used in string representations
(e.g titles/legends of histograms). If pileup reweighting is required, the
``pileup_file`` parameter needs to be set.

.. code-block:: yaml

   input:
     ...
     sample:
       name: Data
       title: 2016 Data
       pileup_file: ""
       run_number: 276243

The trigger subsection describes which trigger is to be used for this dataset.
As the sample name and title, the trigger counterparts play a similar role.

.. code-block:: yaml

   input:
     ...
     trigger:
       name: SingleMu
       title: Single Muon


The ``analysis`` section describes which analyzers are to be run.
Global parameters include flags and binning for the analyzers (``do_fit``,
``pu_bins``). These can also be specified later separately for each analyzer if
required.

.. code-block:: yaml

   analysis:
     do_fit: False
     pu_bins: 0,13,20,999

The analyzers subsection of ``analysis`` is a list of all analyzers to be run.
These analyzers have to satisfy the same API as
``cmsl1t.analyzers.BaseAnalyzer`` and be visible in the `PYTHONPATH`.

.. code-block:: yaml

   analysis:
     ...
     analyzers:
       - cmsl1t.analyzers.demo_analyzer

Modifiers are a way to enrich the event content by attaching objects to the
event itself. E.g. ``cmsl1t.recalc.met.l1MetNot28`` reads in
``event.caloTowers`` and creates a new object, ``event.l1MetNot28``, that can
then be accessed by all analyzers.

.. code-block:: yaml

   analysis:
     ...
     modifiers:
       - cmsl1t.recalc.met.l1MetNot28:
           in: event.caloTowers
           out: event.l1MetNot28
       - cmsl1t.recalc.met.l1MetNot28HF:
           in: event.caloTowers
           out: event.l1MetNot28HF

Next, you can specify if you want progress information (e.g. a progress bar)
and how often this information is updated (``report_every`` in units of
events).

.. code-block:: yaml

   analysis:
     ...
     progress_bar:
       report_every: 1000
     # or to switch it off
     # progress_bar:
     #   enable: False


And finally the output section describes where the output, usually ROOT files,
is stored. The ```template`` entry is composed of a list of paths that are
joined to create the full output file. The template expects the following named
parameters:

* ``date``
* ``sample_name``
* ``run_number``
* ``trigger_name``

which are automatically filled by the config parser


.. code-block:: yaml

   output:
     # template is a list here that is joined (os.path.join) in the config
     # parser
     template:
        - benchmark/new
        - "{date}_{sample_name}_run-{run_number}_{trigger_name}"
'''
from __future__ import print_function
import yaml
import os
from datetime import datetime
import logging
from cmsl1t.utils import module
from copy import deepcopy


logger = logging.getLogger(__name__)
TODAY = datetime.now().timetuple()


def get_unique_out_dir(outdir=None, revision=1):
    full_outdir = outdir + "-rev_{rev}".format(rev=revision)
    if os.path.isdir(full_outdir):
        return get_unique_out_dir(outdir, revision + 1)
    return full_outdir


def resolve_file_paths(paths):
    from cmsl1t.utils.root_glob import glob
    all_files = []
    for p in paths:
        all_files.extend(glob(p))
    return all_files


class ConfigParser(object):
    SECTIONS = ['general', 'input', 'analysis', 'output']

    def __init__(self):
        self.config = {}
        self.config_errors = []

    def read(self, input_file):
        cfg = yaml.load(input_file)
        self._read_config(cfg)

    def _read_config(self, cfg):
        cfg['general'] = dict(version=cfg['version'], name=cfg['name'])
        del cfg['version'], cfg['name']

        input_files = cfg['input']['files']
        try:
            input_files = resolve_file_paths(input_files)
        except Exception, e:
            msg = 'Could not resolve file paths:' + str(e)
            logger.exception(msg)
            raise IOError(msg)
        cfg['input']['files'] = input_files
        self.config = cfg

        if not self.is_valid():
            msg = '\n'.join(self.config_errors)
            logger.exception(msg)
            raise IOError(msg)

        try:
            self.__fill_output_template()
        except Exception, e:
            msg = 'Could fill out output template:' + str(e)
            logger.exception(msg)
            raise IOError(msg)

    def sections(self):
        return self.config.keys()

    def options(self, section):
        return self.config[section].keys()

    def get(self, section, option):
        return self.config[section][option]

    def try_get(self, section, option, default=None):
        if section in self.config:
            if option in self.config[section]:
                return self.config[section][option]
        return default

    def is_valid(self):
        results = [self.validate_sections()]
        results += [self.validate_input_files()]
        results += [self.validate_analyzers()]
        results += [self.validate_modifiers()]
        return all(results)

    def validate_sections(self):
        expectedSections = sorted(ConfigParser.SECTIONS)
        sections = sorted(self.config.keys())
        hasValidSections = expectedSections == sections
        if hasValidSections is not True:
            msg = 'Configuration has missing or invalid sections.\n'
            msg += self.__section_format(
                self.__compare_sections(expectedSections, sections))
            self.config_errors += [msg]
        return hasValidSections

    def __section_format(self, sections):
        section_template = ['  - {}' for _ in sections]
        section_template = '\n'.join(section_template)
        return section_template.format(*sections)

    def __compare_sections(self, expected, current):
        expected = set(expected)
        current = set(current)
        missing = expected.difference(current)
        invalid = current.difference(expected)
        decorated_sections = []
        for e in expected:
            if e in missing:
                decorated_sections.append(e + ' (missing)')
            else:
                decorated_sections.append(e)
        for i in invalid:
            decorated_sections.append(i + ' (invalid)')
        return sorted(decorated_sections)

    def validate_input_files(self):
        input_files = self.config['input']['files']
        if not input_files:
            msg = "Could not find any existing files.\n"
            msg += "Given files:\n"
            msg += '\n'.join(self.config['input']['files'])
            self.config_errors += [msg]
        return input_files != []

    def validate_analyzers(self):
        return self.__validate_module_imports(['analysis', 'analyzers'])

    def validate_modifiers(self):
        return self.__validate_module_imports(['analysis', 'modifiers'])

    def __validate_module_imports(self, config_keys):
        modules = deepcopy(self.config)
        for key in config_keys:
            if key in modules:
                modules = modules[key]
            else:
                msg = "Cannot find required config section: "
                msg += "::".join(config_keys)
                self.config_errors.append(msg)
                return False
        msg = []
        results = []
        for m in modules:
            if isinstance(m, dict):
                m = m.keys()[0]
            if not module.exists(m):
                msg += ['Module {0} does not exist!'.format(m)]
                results += [False]
            else:
                results += [True]
        if msg:
            self.config_errors.append('\n'.join(msg))
        return all(results)

    def __repr__(self):
        return self.config.__repr__()

    def __fill_output_template(self):
        cfg = self.config
        template = os.path.join(*cfg['output']['template'])

        date = '{y}{m:02d}{d:02d}'.format(
            y=TODAY.tm_year, m=TODAY.tm_mon, d=TODAY.tm_mday)
        sample_name = cfg['input']['sample']['name']
        trigger_name = cfg['input']['trigger']['name']
        run_number = cfg['input']['run_number']

        ouput_folder = template.format(
            date=date, sample_name=sample_name, trigger_name=trigger_name,
            run_number=run_number)
        cfg['output']['folder'] = get_unique_out_dir(ouput_folder)

    def describe(self):
        return __doc__


if __name__ == '__main__':
    config = ConfigParser()
    config.read('config/demo.yaml')
    print(config)
    print()
    print('Sections', config.sections())
    for section in config.sections():
        print('Section', section, 'has options', config.options(section))
        for option in config.options(section):
            print('>> {} = {}'.format(option, config.get(section, option)))
    print()
    print(config.is_valid())
