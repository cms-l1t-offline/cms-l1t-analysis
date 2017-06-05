from __future__ import print_function
from cmsl1t.hist.hist_collection import HistogramCollection
from cmsl1t.hist.factory import HistFactory
import cmsl1t.hist.binning as bn

from rootpy.plotting import Canvas, Legend, HistStack
from cmsl1t.utils.draw import draw


class EfficiencyPlot():
    def build(self, online_label, offline_label,
              pileup_bins, thresholds, n_bins, low, high):
        """ This is not in an init function so that we can by-pass this in the
        case where we reload things from disk """
        self.online_label = online_label
        self.offline_label = offline_label
        self.pileup_bins = bn.Sorted(pileup_bins, use_everything_bin=True)
        self.thresholds = bn.GreaterThan(thresholds, use_everything_bin=True)
        self.yields = HistogramCollection([self.pileup_bins, self.thresholds],
                                          "Hist1D", n_bins, low, high)

    def reload(self):
        """ Reload histograms from existing files on disk """
        pass

    def fill(self, pileup, online, offline):
        self.yields[pileup, online].fill(offline)

    def draw(self, with_fits=True):
        # Calclate the efficiency for each threshold
        self.__fill_turnons(with_fits)

        # Overlay the "all" pile-up bin for each threshold
        all_pileup_effs = self.turnons.get_bin_contents([bn.Base.everything])
        # Really need a better way to do this
        hists = [all_pileup_effs.get_bin_contents(key)
                 for key in all_pileup_effs.iter_all()
                 if isinstance(key, int)]
        self.__make_overlay("all_thresholds", hists)

        # Overlay individual pile-up bins for each threshold

        # Produce the fit summary plot
        if with_fits:
            self.__summarize_fits()

    def __fill_turnons(self, with_fits):
        # Boiler plate to convert a given distribution to a turnon
        Eff_factory = HistFactory("Efficiency")

        def make_eff(pileup_bin, threshold_bin):
            total = self.yields.get_bin_contents([pileup_bin, bn.Base.everything])
            passed = self.yields.get_bin_contents([pileup_bin, threshold_bin])
            turnon = Eff_factory.build(passed, total)
            if with_fits:
                self.__fit_one_turnon(pileup_bin, threshold_bin, turnon)
            return turnon

        # Actually make the turnons
        self.turnons = HistogramCollection([self.pileup_bins, self.thresholds],
                                           make_eff)

    def __make_overlay(self, file_kernel, hists):
        # Need a canvas
        canvas = Canvas()

        # Draw each turnon (with fit)
        draw(hists)

        # Add labels
        # Add a legend

        # Save canvas to file
        canvas.SaveAs(file_kernel + ".png")

    def __summarize_fits(self):
        pass


    def __fit_one_turnon(self, pileup_bin, threshold_bin, turnon):
        pass
