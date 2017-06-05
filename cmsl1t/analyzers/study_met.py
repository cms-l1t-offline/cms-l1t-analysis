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

        self.eff_fullMet = EfficiencyPlot()

    def prepare_for_events(self, reader):
        puBins = range(0, 50, 10) + [999]
        thresholds = [70, 90, 110]

        self.eff_fullMet.build("MET", "PF MET",
                               puBins, thresholds, 50, 0, 300)

        return True

    def reload_histograms(self, input_file):
        self.eff_fullMet.reload()
        return True

    def fill_histograms(self, entry, event):
        pileup = event.nVertex
        if pileup < 5 or not event.passesMETFilter():
            return True

        offlineMetBE = event.sums.caloMetBE

        onlineMet = recalc.l1MetNot28(event.caloTowers).mag
        self.eff_fullMet.fill(pileup, offlineMetBE, onlineMet)

        return True

    def write_histograms(self):
        # self.eff_fullMet.to_root(self.get_histogram_filename())
        return True

    def make_plots(self):
        self.eff_fullMet.draw()
        return True
