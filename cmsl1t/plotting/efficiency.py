from __future__ import print_function
from cmsl1t.plotting.base import BasePlotter
from cmsl1t.hist.hist_collection import HistogramCollection
from cmsl1t.hist.factory import HistFactory
import cmsl1t.hist.binning as bn
from cmsl1t.utils.draw import draw, label_canvas
from cmsl1t.utils.fit_efficiency import fit_efficiency
import numpy as np

from rootpy.plotting import Legend, HistStack, Efficiency
from rootpy.context import preserve_current_style
from rootpy import asrootpy, ROOT


# Hack to fix Efficiency.__iadd__ for now
# TODO: Remove when we update rootpy to >0.9.2
def my_iadd(self, other):
    super(Efficiency, self).Add(other)
    return self


# TODO: Remove when we update rootpy to >0.9.2
setattr(Efficiency, "__iadd__", my_iadd)


class EfficiencyPlot(BasePlotter):
    def __init__(self, online_name, offline_name):
        name = ["efficiency", online_name, offline_name]
        super(EfficiencyPlot, self).__init__("__".join(name))
        self.online_name = online_name
        self.offline_name = offline_name

    def create_histograms(self,
                          online_title, offline_title,
                          pileup_bins, thresholds,
                          n_bins, low, high=400, legend_title=""):
        """ This is not in an init function so that we can by-pass this in the
        case where we reload things from disk """
        self.online_title = online_title
        self.offline_title = offline_title
        self.pileup_bins = bn.Sorted(pileup_bins, "pileup",
                                     use_everything_bin=True)
        self.thresholds = bn.GreaterThan(thresholds, "threshold")
        self.legend_title = legend_title

        name = ["efficiency", self.online_name, self.offline_name]
        name += ["thresh_{threshold}", "pu_{pileup}"]
        name = "__".join(name)
        title = " ".join([self.online_name, " in PU bin: {pileup}",
                          "and passing threshold: {threshold}"])
        self.filename_format = name

        def make_efficiency(labels):
            this_name = "efficiency" + name.format(**labels)
            this_title = title.format(**labels)
            '''Checking type of 'low' to see whether it's int (x-range minimum)
                    or array (bin edges) for constructing TEfficiency'''
            if isinstance(low, np.ndarray):
                eff = asrootpy(ROOT.TEfficiency(this_name, this_title,
                                            n_bins, low))
            else:
                eff = asrootpy(ROOT.TEfficiency(this_name, this_title,
                                            n_bins, low, high))
            eff.drawstyle = "EP"
            return eff
        self.efficiencies = HistogramCollection([self.pileup_bins, self.thresholds],
                                                make_efficiency)

    def fill(self, pileup, online, offline):
        efficiencies = {(pu, thresh): eff
                        for (pu,), thresholds in self.efficiencies[pileup].items()
                        for thresh, eff in thresholds.items()}
        for (pu_bin, threshold_bin), efficiency in efficiencies.items():
            threshold = self.thresholds.get_bin_center(threshold_bin)
            passed = False
            if isinstance(threshold, str):
                continue
            elif online > threshold:
                passed = True
            efficiency.fill(passed, offline)

    def draw(self, with_fits=True):
        # Fit the efficiencies if requested
        if with_fits:
            self.__fit_efficiencies()

        # Overlay the "all" pile-up bin for each threshold
        all_pileup_effs = self.efficiencies.get_bin_contents([bn.Base.everything])
        hists = []
        labels = []
        fits = []
        for threshold in all_pileup_effs.iter_all():
            if not isinstance(threshold, int):
                continue
            hist = all_pileup_effs.get_bin_contents(threshold)
            hist.drawstyle = "EP"
            hists.append(hist)
            labels.append(str(self.online_title) + " > " + str(self.thresholds.bins[threshold]) + " (GeV)")
            if with_fits:
                fits.append(self.fits.get_bin_contents([bn.Base.everything, threshold]))
        self.__make_overlay("all", "all", hists, fits, labels, self.online_title)

        # Overlay individual pile-up bins for each threshold
        for threshold in self.thresholds:
            hists = []
            labels = []
            fits = []
            for pileup in self.pileup_bins:
                if not isinstance(pileup, int):
                    continue
                hist = self.efficiencies.get_bin_contents([pileup, threshold])
                hist.drawstyle = "EP"
                hists.append(hist)
                if with_fits:
                    fits.append(self.fits.get_bin_contents([pileup, threshold]))
                labels.append(str(self.pileup_bins.bins[pileup]))
            self.__make_overlay(pileup, threshold, hists, fits, labels, "PU bin")

        # Produce the fit summary plot
        if with_fits:
            self.__summarize_fits()

    def __fit_efficiencies(self):
        def make_fit(labels):
            pileup_bin = labels["pileup"]
            threshold_bin = labels["threshold"]
            efficiency = self.efficiencies.get_bin_contents([pileup_bin, threshold_bin])
            params = fit_efficiency(efficiency, self.thresholds.get_bin_center(threshold_bin))
            return params

        # Actually make the efficiencies
        self.fits = HistogramCollection([self.pileup_bins, self.thresholds],
                                        make_fit)

    def __make_overlay(self, pileup, threshold, hists, fits, labels, header):
        with preserve_current_style():
            # Draw each efficiency (with fit)
            canvas = draw(hists, draw_args={"xtitle": self.offline_title,
                                            "ytitle": "Efficiency"})
            if len(fits) > 0:
                for fit, hist in zip(fits, hists):
                    fit["asymmetric"].linecolor = hist.GetLineColor()
                    fit["asymmetric"].Draw("same")

            # Add labels
            label_canvas()

            # Add a legend
            legend = Legend(len(hists), header=self.legend_title,
                            topmargin=0.35, rightmargin=0.3, leftmargin=0.7, textsize=0.035, entryheight=0.035)
            for hist, label in zip(hists, labels):
                legend.AddEntry(hist, label)
            legend.SetBorderSize(0)
            legend.Draw()

            # Save canvas to file
            name = self.filename_format.format(pileup=pileup,
                                               threshold=threshold)
            self.save_canvas(canvas, name)

    def __summarize_fits(self):
        """ Implement this to show fit evolution plots """
        # TODO: Implement this __summarize_fits methods
        pass

    def _is_consistent(self, new):
        """
        Check the two plotters are the consistent, so same binning and same axis names
        """
        return all([self.pileup_bins.bins == new.pileup_bins.bins,
                    self.thresholds.bins == new.thresholds.bins,
                    self.online_name == new.online_name,
                    self.offline_name == new.offline_name,
                    ])

    def _merge(self, other):
        """
        Merge another plotter into this one
        """
        self.efficiencies += other.efficiencies
        return self.efficiencies
