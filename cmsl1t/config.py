from __future__ import print_function
import yaml
import os
from datetime import datetime

TODAY = datetime.now().timetuple()


def validate_sections(expectedSections, configPart):
    return sorted(expectedSections) == sorted(configPart.keys())


def get_unique_out_dir(outdir=None, revision=1):
    full_outdir = outdir + "-rev_{rev}".format(rev=revision)
    if os.path.isdir(full_outdir):
        return get_unique_out_dir(outdir, revision + 1)
    return full_outdir


class ConfigParser(object):
    SECTIONS = ['general', 'input', 'analysis', 'output']

    def __init__(self):
        self.config = {}

    def read(self, input_file):
        cfg = yaml.load(input_file)
        cfg['general'] = dict(version=cfg['version'], name=cfg['name'])
        del cfg['version'], cfg['name']

        if not validate_sections(ConfigParser.SECTIONS, cfg):
            # TODO: improve
            raise IOError('Invalid config')

        self.config = cfg
        self.__fill_output_template()

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
        return validate_sections(ConfigParser.SECTIONS, self.config)

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
