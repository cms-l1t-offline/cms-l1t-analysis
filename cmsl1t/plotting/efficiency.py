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

    def create_histograms(
            self, online_title, offline_title, pileup_bins, thresholds,
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
                eff = asrootpy(
                    ROOT.TEfficiency(this_name, this_title, n_bins, low)
                )
                self.x_max = 2000
            else:
                eff = asrootpy(
                    ROOT.TEfficiency(this_name, this_title, n_bins, low, high)
                )
                self.x_max = high
            eff.drawstyle = "HIST"
            return eff
        self.efficiencies = HistogramCollection(
            [self.pileup_bins, self.thresholds],
            make_efficiency
        )

    def fill(self, pileup, offline, online):
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

    def draw(self, with_fits=False):
        # Fit the efficiencies if requested
        if with_fits:
            self.__fit_efficiencies()

        # Overlay the "all" pile-up bin for each threshold
        all_pileup_effs = self.efficiencies.get_bin_contents(
            [bn.Base.everything])
        hists = []
        labels = []
        fits = []
        label_template = '{online_title} > {threshold} GeV'
        for threshold in all_pileup_effs.iter_all():
            if not isinstance(threshold, int):
                continue
            hist = all_pileup_effs.get_bin_contents(threshold)
            hist.drawstyle = "P"
            hists.append(hist)

            label = label_template.format(
                online_title=self.online_title,
                threshold=self.thresholds.bins[threshold],
            )
            labels.append(label)
            if with_fits:
                fits.append(self.fits.get_bin_contents(
                    [bn.Base.everything, threshold]))
        self.__make_overlay(
            "all", "all", hists, fits, labels, self.online_title,
        )

        # Overlay individual pile-up bins for each threshold
        #for threshold in self.thresholds:
        #    hists = []
        #    labels = []
        #    fits = []
        #    for pileup in self.pileup_bins:
        #        if not isinstance(pileup, int):
        #            continue
        #        hist = self.efficiencies.get_bin_contents([pileup, threshold])
        #        hist.drawstyle = "P"
        #        hists.append(hist)
        #        if with_fits:
        #            fits.append(self.fits.get_bin_contents(
        #                [pileup, threshold]))
        #        labels.append(str(self.pileup_bins.bins[pileup]))
        #    self.__make_overlay(pileup, threshold, hists,
        #                        fits, labels, "PU bin")

        # Produce the fit summary plot
        if with_fits:
            self.__summarize_fits()

    def overlay_with_emu(self, emu_plotter, with_fits=False):
        # Fit the efficiencies if requested
        if with_fits:
            self.__fit_efficiencies()

        # Overlay the "all" pile-up bin for each threshold
        all_pileup_effs = self.efficiencies.get_bin_contents(
            [bn.Base.everything])
        emu_pileup_effs = emu_plotter.efficiencies.get_bin_contents(
            [bn.Base.everything])
        hists = []
        labels = []
        fits = []
        label_template = '{online_title} > {threshold} GeV'

        ROOT.gStyle.SetErrorX(0.)

        for threshold in all_pileup_effs.iter_all():
            if not isinstance(threshold, int):
                continue
            hist = all_pileup_effs.get_bin_contents(threshold)
            hist.drawstyle = "P"
            hists.append(hist)

            label = label_template.format(
                online_title=self.online_title,
                threshold=self.thresholds.bins[threshold],
            )
            labels.append(label)
            if with_fits:
                fits.append(self.fits.get_bin_contents(
                    [bn.Base.everything, threshold]))

        for threshold in emu_pileup_effs.iter_all():
            if not isinstance(threshold, int):
                continue
            hist = emu_pileup_effs.get_bin_contents(threshold)
            hist.drawstyle = "P"
            hist.markerstyle = 23
            hists.append(hist)

            label = label_template.format(
                online_title=emu_plotter.online_title + ' Emu',
                threshold=emu_plotter.thresholds.bins[threshold],
            )
            labels.append(label)
            if with_fits:
                fits.append(emu_plotter.fits.get_bin_contents(
                    [bn.Base.everything, threshold]))

        self.__make_overlay(
            "all", "all_overlay_with_Emu", hists, fits, labels, self.online_title,
        )

        '''
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
                    fits.append(self.fits.get_bin_contents(
                        [pileup, threshold]))
                labels.append(str(self.pileup_bins.bins[pileup]))
            self.__make_overlay(pileup, threshold, hists,
                                fits, labels, "PU bin")
        '''
        # Produce the fit summary plot
        if with_fits:
            self.__summarize_fits()

    def __fit_efficiencies(self):
        def make_fit(labels):
            pileup_bin = labels["pileup"]
            threshold_bin = labels["threshold"]
            efficiency = self.efficiencies.get_bin_contents(
                [pileup_bin, threshold_bin])
            params = fit_efficiency(
                efficiency, self.thresholds.get_bin_center(threshold_bin))
            return params

        # Actually make the efficiencies
        self.fits = HistogramCollection([self.pileup_bins, self.thresholds],
                                        make_fit)

    def __make_overlay(self, pileup, threshold, hists, fits, labels, header):
        with preserve_current_style():
            name = self.filename_format.format(pileup=pileup,
                                               threshold=threshold)
            # Draw each efficiency (with fit)
            if 'Jet' in name and 'HiRange' in name:
                xlimits = [20,2000]
                canvas = draw(hists, draw_args={"xtitle": self.offline_title,
                                                "ytitle": "Efficiency",
                                                "xlimits": xlimits})
            else:
                canvas = draw(hists, draw_args={"xtitle": self.offline_title,
                                                "ytitle": "Efficiency"})
            if len(fits) > 0:
                for fit, hist in zip(fits, hists):
                    fit["asymmetric"].linecolor = hist.GetLineColor()
                    fit["asymmetric"].Draw("same")

            # Add labels
            label_canvas()

            # Add a legend
            legend = Legend(
                len(hists),
                header=self.legend_title,
                topmargin=0.35,
                rightmargin=0.3,
                leftmargin=0.7,
                textsize=0.025,
                entryheight=0.028,
            )

            for hist, label in zip(hists, labels):
                legend.AddEntry(hist, label)
            legend.SetBorderSize(0)
            legend.Draw()

            xmax = self.x_max


            if("HT" in name):
                xmax = 800
                xmin = 30
            if("MET" in name):
                xmin = 0
                xmax = 400
            if("Jet" in name):
                xmin = 20
                xmax = 400
            if("HiRange" in name):
                xmax=2000


            for val in [0.25, 0.5, 0.75, 0.95, 1.]:
                line = ROOT.TLine(xmin, val, xmax, val)
                line.SetLineStyle("dashed")
                line.SetLineColor(15)
                line.Draw()

            for val in range(100, xmax, 100):
                line = ROOT.TLine(val, 0., val, 1.)
                line.SetLineStyle("dashed")
                line.SetLineColor(15)
                line.Draw()

            # Save canvas to file
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
