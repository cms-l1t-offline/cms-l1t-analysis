from __future__ import print_function
from cmsl1t.plotting.base import BasePlotter
from cmsl1t.hist.hist_collection import HistogramCollection
from cmsl1t.hist.factory import HistFactory
import cmsl1t.hist.binning as bn
from cmsl1t.utils.draw import draw, label_canvas
from cmsl1t.recalc.resolution import get_resolution_function

from rootpy.context import preserve_current_style
from rootpy.plotting import Legend
from rootpy import ROOT


class ResolutionPlot(BasePlotter):
    def __init__(self, resolution_type, online_name, offline_name):
        name = ["resolution", online_name, offline_name]
        super(ResolutionPlot, self).__init__("__".join(name))
        self.online_name = online_name
        self.offline_name = offline_name
        self.resolution_method = get_resolution_function(resolution_type)

    def create_histograms(self,
                          online_title, offline_title,
                          pileup_bins, n_bins, low, high, legend_title=""):
        """ This is not in an init function so that we can by-pass this in the
        case where we reload things from disk """
        self.online_title = online_title
        self.offline_title = offline_title
        self.legend_title = legend_title
        self.pileup_bins = bn.Sorted(pileup_bins, "pileup",
                                     use_everything_bin=True)

        name = ["resolution", self.online_name, self.offline_name, "pu_{pileup}"]
        name = "__".join(name)
        title = " ".join([self.online_name, "vs.", self.offline_name, "in PU bin: {pileup}"])
        title = ";".join([title, self.offline_title, self.online_title])
        self.plots = HistogramCollection([self.pileup_bins],
                                         "Hist1D", n_bins, low, high,
                                         name=name, title=title)
        self.filename_format = name

    def fill(self, pileup, offline, online):
        difference = self.resolution_method(online, offline)
        self.plots[pileup].fill(difference)

    def draw(self, with_fits=False):
        hists = []
        labels = []
        fits = []
        for (pile_up, ), hist in self.plots.flat_items_all():
            if pile_up == bn.Base.everything:
                #hist.linestyle = "dashed"
                hist.drawstyle = "P"
                label = "All PU"
            elif isinstance(pile_up, int):
                hist.drawstyle = "P"
                if self.pileup_bins.get_bin_upper(pile_up) < 500:
                    label = "{:.0f} \\leq PU < {:.0f}".format(self.pileup_bins.get_bin_lower(pile_up), self.pileup_bins.get_bin_upper(pile_up))
                else:
                    label = "{:.0f} < PU".format(self.pileup_bins.get_bin_lower(pile_up))
            else:
                continue
            hist.SetMarkerSize(0.5)
            hist.SetLineWidth(1)
            hists.append(hist)
            labels.append(label)
            if with_fits:
                fits.append(self.fits.get_bin_contents([pile_up]))
        #self.__make_overlay(hists, fits, labels, "Number of events")

        normed_hists = [hist / hist.integral() if hist.integral() != 0 else hist.Clone() for hist in hists]

        self.__make_overlay(normed_hists, fits, labels, "a.u.", "__shapes")


    def overlay_with_emu(self, emu_plotter, with_fits=False):
        hists = []
        labels = []
        fits = []
        for (pile_up, ), hist in self.plots.flat_items_all():
            if pile_up == bn.Base.everything:
                hist.SetLineStyle(1)
                hist.drawstyle = "P"
                label = "HW, all PU"
            else:
                continue
            hist.SetMarkerSize(0.5)
            hist.SetLineWidth(1)
            hists.append(hist)
            labels.append(label)

        for (pile_up, ), hist in emu_plotter.plots.flat_items_all():
            if pile_up == bn.Base.everything:
                hist.SetLineStyle(1)
                hist.drawstyle = "P"
                label = "Emu, all PU"
            else:
                continue
            hist.SetMarkerSize(0.5)
            hist.SetLineWidth(1)
            hists.append(hist)
            labels.append(label)

        #self.__make_overlay(hists, fits, labels, "Number of events", "__Overlay_Emu")

        normed_hists = [hist / hist.integral() if hist.integral() != 0 else hist.Clone() for hist in hists]

        self.__make_overlay(normed_hists, fits, labels, "a.u.", "__shapes__Overlay_Emu")

    def __make_overlay(self, hists, fits, labels, ytitle, suffix=""):
        with preserve_current_style():
            # Draw each resolution (with fit)
            xtitle = self.resolution_method.label.format(on=self.online_title, off=self.offline_title)
            name = self.filename_format.format(pileup="all")
            for hist in hists:
                hist.GetYaxis().SetRangeUser(0,0.1)
                hist.GetYaxis().SetTitleOffset(1.4)
                canvas = draw(hists, draw_args={"xtitle": xtitle, "ytitle": ytitle})
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
                topmargin=0.45,
                rightmargin=0.2,
                leftmargin=0.8,
                textsize=0.03,
                entryheight=0.03,
            )
            for hist, label in zip(hists, labels):
                legend.AddEntry(hist, label)
            legend.SetBorderSize(0)
            legend.Draw()

            ymax = 1.2 * hists[-1].GetMaximum()

            line = ROOT.TLine(0., 0., 0., ymax)
            #line.SetLineStyle("dashed")
            line.SetLineColor(15)
            #line.Draw()

            # Save canvas to file
            self.save_canvas(canvas, name + suffix)

    def _is_consistent(self, new):
        """
        Check the two plotters are the consistent, so same binning and same axis names
        """
        return all([self.pileup_bins.bins == new.pileup_bins.bins,
                    self.resolution_method == new.resolution_method,
                    self.online_name == new.online_name,
                    self.offline_name == new.offline_name,
                    ])

    def _merge(self, other):
        """
        Merge another plotter into this one
        """
        self.plots += other.plots
        return self.plots
