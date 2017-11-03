from cmsl1t.config import (ConfigParser, resolve_file_paths)
import yaml

from nose.tools import (raises, assert_equal, assert_almost_equal,
                        assert_raises, assert_true, assert_false)
from nose import with_setup
import pyfakefs.fake_filesystem as fake_fs
import pyfakefs.fake_filesystem_glob as fake_glob

try:
    from unittest.mock import patch  # In Python 3, mock is built-in
except ImportError:
    from mock import patch

TEST_CONFIG = """
version: 0.0.1
name: Benchmark

input:
  files:
    - /tmp/l1t/L1Ntuple_*.root
  sample:
    name: Data
    title: 2016 Data
  trigger:
    name: SingleMu
    title: Single Muon
  pileup_file: ""
  run_number: 276243

analysis:
  do_fit: False
  pu_type: 0PU12,13PU19,20PU
  pu_bins: 0,13,20,999
  analyzers:
    - cmsl1t.analyzers.demo_analyzer
  producers:
    - cmsl1t.recalc.met.l1MetNot28:
        in: event.caloTowers
        out: event.l1MetNot28
    - cmsl1t.recalc.met.l1MetNot28HF:
        in: event.caloTowers
        out: event.l1MetNot28HF
  progress_bar:
    report_every: 1000
  # or to switch it off
  # progress_bar:
  #   enable: False

output:
  # template is a list here that is joined (os.path.join) in the config parser
  template:
     - benchmark/new
     - "{date}_{sample_name}_run-{run_number}_{trigger_name}"
"""


# Create a faked file system
fs = fake_fs.FakeFilesystem()

# Do some setup on the faked file system
ALL_EXISTING_FILES = [
    '/tmp/l1t/L1Ntuple_1.root',
    '/tmp/l1t/L1Ntuple_2.root',
    '/tmp/l1t/L1Ntuple_3.root',
]
for f in ALL_EXISTING_FILES:
    fs.CreateFile(f)

glob = fake_glob.FakeGlobModule(fs)


def setup_func():
    "set up test fixtures"


def teardown_func():
    "tear down test fixtures"


def test_general_section():
    with patch('glob.glob', glob.glob):
        parser = ConfigParser()
        parser._read_config(yaml.load(TEST_CONFIG))
        assert_equal(parser.get('general', 'version'), '0.0.1')
        assert_equal(parser.get('general', 'name'), 'Benchmark')


def test_invalid_section():
    with patch('glob.glob', glob.glob):
        parser = ConfigParser()
        config_with_invalid_section = yaml.load(
            TEST_CONFIG.replace('analysis:', 'ryan:'))
        assert_raises(IOError, parser._read_config,
                      config_with_invalid_section)


def test_invalid_analyzer():
    with patch('glob.glob', glob.glob):
        parser = ConfigParser()
        config_with_invalid_analyzer = yaml.load(
            TEST_CONFIG.replace('cmsl1t.analyzers.demo_analyzer', 'ben'))
        assert_raises(IOError, parser._read_config,
                      config_with_invalid_analyzer)


def test_invalid_modifier():
    with patch('glob.glob', glob.glob):
        parser = ConfigParser()
        config_with_invalid_analyzer = yaml.load(
            TEST_CONFIG.replace('cmsl1t.recalc.met.l1MetNot28', 'olivier'))
        assert_raises(IOError, parser._read_config,
                      config_with_invalid_analyzer)


def test_resolve_file_paths():
    with patch('glob.glob', glob.glob):
        input_files = resolve_file_paths(['/tmp/l1t/L1Ntuple_*.root'])
        assert_equal(input_files, ALL_EXISTING_FILES)


def test_resolve_file_paths_missing_file():
    with patch('glob.glob', glob.glob):
        input_files = resolve_file_paths(
            ['/tmp/l1t/L1Ntuple_*.root', '/tmp/missingFile'])
        assert_equal(input_files, ALL_EXISTING_FILES)


def test_input_section():
    with patch('glob.glob', glob.glob):
        parser = ConfigParser()
        parser._read_config(yaml.load(TEST_CONFIG))
        assert_equal(parser.get('input', 'files'), ALL_EXISTING_FILES)
        assert_equal(parser.get('input', 'sample'), {
                     'name': 'Data', 'title': '2016 Data'})


def test_input_section_missing_files():
    with patch('glob.glob', glob.glob):
        parser = ConfigParser()
        bad_input_files = TEST_CONFIG.replace(
            '/tmp/l1t/L1Ntuple_*.root', '/tmp/missingFile')
        config_with_missing_files = yaml.load(bad_input_files)

        assert_raises(IOError, parser._read_config, config_with_missing_files)
