from __future__ import print_function
from cmsl1t.hist.hist_collection import HistogramCollection
from cmsl1t.hist.factory import HistFactory
import cmsl1t.hist.binning as bn
from cmsl1t.utils.draw import draw, label_canvas
from cmsl1t.io import to_root

from rootpy.plotting import Legend, HistStack
from rootpy.context import preserve_current_style


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
        filename = ["eff", online_label, offline_label,
                    "thresh_{thresh}", "pu_{pileup}"]
        self.filename_format = "{outdir}/" + "-".join(filename) + ".{fmt}"

    def set_plot_output_cfg(self, outdir, fmt):
        self.output_dir = outdir
        self.output_format = fmt

    def from_root(self, filename):
        """ Reload histograms from existing files on disk """
        pass

    def to_root(self, filename):
        """ Write histograms to disk """
        to_write = [self, self.yields]
        if hasattr(self,"turnons"):
            to_write += [self.turnons]
        to_root(to_write, filename)

    def fill(self, pileup, online, offline):
        self.yields[pileup, online].fill(offline)

    def draw(self, with_fits=True):
        # Calclate the efficiency for each threshold
        self.__fill_turnons(with_fits)

        # Overlay the "all" pile-up bin for each threshold
        all_pileup_effs = self.turnons.get_bin_contents([bn.Base.everything])
        hists = [all_pileup_effs.get_bin_contents(key)
                 for key in all_pileup_effs.iter_all()
                 if isinstance(key, int)]
        self.__make_overlay("all", "all", hists)

        # Overlay individual pile-up bins for each threshold
        for threshold in self.thresholds:
            hists = []
            for pileup in self.pileup_bins:
                hists.append(self.turnons.get_bin_contents([pileup, threshold]))
            self.__make_overlay(pileup, threshold, hists)

        # Produce the fit summary plot
        if with_fits:
            self.__summarize_fits()

    def __fill_turnons(self, with_fits):

        # Boiler plate to convert a given distribution to a turnon
        def make_eff(pileup_bin, threshold_bin):
            total = self.yields.get_bin_contents([pileup_bin, bn.Base.everything])
            passed = self.yields.get_bin_contents([pileup_bin, threshold_bin])
            turnon = passed.Clone(passed.name + "turnon")
            turnon.Divide(total)
            if with_fits:
                self.__fit_one_turnon(pileup_bin, threshold_bin, turnon)
            return turnon

        # Actually make the turnons
        self.turnons = HistogramCollection([self.pileup_bins, self.thresholds],
                                           make_eff)

    def __make_overlay(self, pileup, threshold, hists):
        with preserve_current_style():
            # Draw each turnon (with fit)
            canvas = draw(hists, draw_args={"xtitle":self.offline_label,
                                            "ytitle":self.online_label})

            # Add labels
            label_canvas()

            # Add a legend
            legend = Legend(len(hists))
            for hist in hists:
                legend.AddEntry(hist)
            legend.Draw()

            # Save canvas to file
            filename = self.filename_format
            filename = filename.format(outdir=self.output_dir,
                                       pileup=pileup,
                                       thresh=threshold,
                                       fmt="png")
            canvas.SaveAs(filename)

    def __summarize_fits(self):
        pass

    def __fit_one_turnon(self, pileup_bin, threshold_bin, turnon):
        pass
