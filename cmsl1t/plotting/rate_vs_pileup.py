from __future__ import print_function
import pandas as pd

from cmsl1t.plotting.base import BasePlotter
from cmsl1t.hist.hist_collection import HistogramCollection
import cmsl1t.hist.binning as bn
from cmsl1t.utils.draw import draw, label_canvas
from cmsl1t.recalc.resolution import get_resolution_function

from rootpy.context import preserve_current_style
from rootpy.plotting import Legend


class RateVsPileupPlot(BasePlotter):

    def __init__(self, online_name):
        name = ["rate_vs_pileup", online_name]
        super(RateVsPileupPlot, self).__init__("__".join(name))
        self.online_name = online_name

    def create_histograms(self,
                          online_title,
                          thresholds, n_bins, low, high, legend_title=""):
        """ This is not in an init function so that we can by-pass this in the
        case where we reload things from disk """
        self.online_title = online_title
        self.thresholds = thresholds
        self.thresholds = bn.GreaterThan(thresholds, "threshold", True)
        self.legend_title = legend_title
        name = ["rate_vs_pileup", self.online_name]
        name += ["thresh_{threshold}"]
        name = "__".join(name)
        title = " ".join([self.online_name, " rate vs pileup",
                          "passing threshold: {threshold}"])
        self.plots = HistogramCollection([self.thresholds],
                                         "Hist1D", n_bins, low, high,
                                         name=name, title=title)

        self.filename_format = name

    def fill(self, pileup, online):
        self.plots[online].fill(pileup)

    def draw(self, with_fits=False):

        for (threshold, ), hist in self.plots.flat_items_all():
            hists = []
            labels = []
            fits = []
            thresholds = []
            if not isinstance(threshold, int):
                continue
            label_template = '{online_title} > {threshold} GeV'
            label = label_template.format(
                online_title=self.online_title,
                threshold=self.thresholds.bins[threshold],
            )
            hist.Divide(self.plots.get_bin_contents([bn.Base.everything]))
            hist.drawstyle = "EP"
            hist.SetMarkerColor(2)
            # if with_fits:
            #    fit = self.fits.get_bin_contents([threshold])
            #    fits.append(fit)
            hists.append(hist)
            labels.append(label)
            thresholds.append(threshold)

            self.__make_overlay(hists, fits, labels, thresholds)

    def overlay(self, other_plotters=None, with_fits=False, comp=False):

        hists = []
        labels = []
        fits = []
        thresholds = []
        suffix = '__emu_overlay'
        titles = ['Hw', 'Emu']
        if comp:
            suffix = '__comparison'
            titles = [other_plotter.comp_title for other_plotter in other_plotters]
            titles.insert(0, self.comp_title)

        for (threshold, ), hist in self.plots.flat_items_all():
            if not isinstance(threshold, int):
                continue
            label_template = '{online_title} > {threshold} GeV'
            label = label_template.format(
                online_title='L1 ' + titles[0],
                threshold=self.thresholds.bins[threshold],
            )
            hist.Divide(self.plots.get_bin_contents([bn.Base.everything]))
            hist.Scale(2855)
            hist.drawstyle = "EP"
            hist.SetMarkerColor(1)
            # if with_fits:
            #    fit = self.fits.get_bin_contents([threshold])
            #    fits.append(fit)
            hists.append(hist)
            labels.append(label)
            thresholds.append(threshold)
        for other_plotter in other_plotters:
            for (threshold, ), hist in other_plotter.plots.flat_items_all():
                if not isinstance(threshold, int):
                    continue
                label_template = '{online_title} > {threshold} GeV'
                label = label_template.format(
                    online_title='L1 ' + titles[other_plotters.index(other_plotter) + 1],
                    threshold=other_plotter.thresholds.bins[threshold],
                )
                hist.Divide(other_plotter.plots.get_bin_contents([bn.Base.everything]))
                hist.Scale(2855)
                hist.drawstyle = "EP"
                hist.SetMarkerColor(2)
                hist.markerstyle = 21 + other_plotters.index(other_plotter)
                # if with_fits:
                #    fit = self.fits.get_bin_contents([threshold])
                #    fits.append(fit)
                hists.append(hist)
                labels.append(label)
                thresholds.append(threshold)

        self.__make_overlay(hists, fits, labels, thresholds, suffix)

    def __make_overlay(self, hists, fits, labels, thresholds, suffix=""):
        with preserve_current_style():
            # Draw each rate vs pileup (with fit)
            xtitle = "< \\mu >"
            ytitle = "Rate (kHz)"
            canvas = draw(hists, draw_args={"xtitle": xtitle, "ytitle": ytitle, "xlimits": (20, 50), "ylimits": (0, 5)})
            if fits:
                for fit, hist in zip(fits, hists):
                    fit["asymmetric"].linecolor = hist.GetLineColor()
                    fit["asymmetric"].Draw("same")

            # Add labels
            label_canvas()

            # Add a legend
            legend = Legend(
                len(hists),
                header=self.legend_title,
                topmargin=0.02,
                leftmargin=0.22,
                rightmargin=0.78,
                textsize=0.025,
                entryheight=0.028,
            )

            for hist, label in zip(hists, labels):
                legend.AddEntry(hist, label)

            legend.SetBorderSize(0)
            legend.Draw()

            # Save canvas to file
            name = self.filename_format.format(threshold=thresholds[0])
            self.save_canvas(canvas, name + suffix)

    def _is_consistent(self, new):
        """
        Check the two plotters are the consistent, so same binning and same axis names
        """
        return all([self.thresholds.bins == new.thresholds.bins,
                    self.online_name == new.online_name,
                    ])

    def _merge(self, other):
        """
        Merge another plotter into this one
        """
        self.plots += other.plots
        return self.plots

    def get_stats(self, summary_bins=[], summary_label=''):
        summary_columns = list(self._summary_columns(summary_bins, summary_label))
        stats = list(self._collect_stats(summary_bins, summary_label))
        df = pd.DataFrame(stats)
        return df[['identifier', 'total', 'overflow'] + summary_columns]

    def _summary_columns(self, summary_bins, summary_label):
        for lower, upper in zip(summary_bins[:-1], summary_bins[1:]):
            yield '{} {}-{}'.format(summary_label, lower, upper)

    def _collect_stats(self, summary_bins, summary_label):
        normalisation = self.plots.get_bin_contents([bn.Base.everything]).integral(overflow=True)
        for (threshold, ), hist in self.plots.flat_items():
            human_readable_threshold = '{0} > {1} GeV'.format(self.online_title, self.thresholds.bins[threshold])
            rhist = hist.rebinned(summary_bins)
            stats = {}
            summary_columns = self._summary_columns(summary_bins, summary_label)
            for summary_column, y in zip(summary_columns, rhist.y()):
                stats[summary_column] = y * normalisation
            total = sum(stats.values())
            overflow = rhist.integral(overflow=True) * normalisation - total
            header = dict(identifier=human_readable_threshold, total=total, overflow=overflow)
            header.update(stats)
            yield header
