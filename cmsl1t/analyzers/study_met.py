"""
Study the MET distibutions and various PUS schemes
"""

from BaseAnalyzer import BaseAnalyzer
from cmsl1t.plotting.efficiency import EfficiencyPlot
from functools import partial
import cmsl1t.recalc.met as recalc
import numpy as np


class Analyzer(BaseAnalyzer):
    def __init__(self, config):
        super(Analyzer, self).__init__("study_met", config)

        self.eff_caloMET_BE = EfficiencyPlot()
        self.all_plots = [self.eff_caloMET_BE]

        file_format = config.try_get('output', 'plot_format', "png")
        for hist in self.all_plots:
            hist.set_plot_output_cfg(self.output_folder, file_format)

    def prepare_for_events(self, reader):
        # TODO: Get these from a common place, and / or the config file
        puBins = range(0, 50, 10) + [999]
        thresholds = [70, 90, 110]

        self.eff_caloMET_BE.build("CaloMETBE", "OfflineMETBE",
                                  "CaloMET BE (GeV)", "Offline MET BE (GeV)",
                                  puBins, thresholds, 50, 0, 300)
        return True

    def reload_histograms(self, input_file):
        return True

    def fill_histograms(self, entry, event):
        pileup = event.nVertex
        if pileup < 5 or not event.passesMETFilter():
            return True

        if len(event.caloTowers) <= 0:
            return True

        offlineMetBE = event.sums.caloMetBE
        onlineMet = recalc.l1MetNot28(event.caloTowers).mag

        self.eff_caloMET_BE.fill(pileup, offlineMetBE, onlineMet)

        return True

    def write_histograms(self):
        for hist in self.all_plots:
            hist.to_root(self.get_histogram_filename())
        return True

    def make_plots(self):
        for plot in self.all_plots:
            plot.draw()
        return True
