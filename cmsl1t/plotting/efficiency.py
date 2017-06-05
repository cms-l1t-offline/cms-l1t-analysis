from __future__ import print_function
import cmsl1t.hist.hist_collection as hist
import cmsl1t.hist.binning as bn

from rootpy.plotting import Canvas, Legend
from rootpy.plotting.utils import draw


class EfficiencyPlot():
    def build(self, online_label, offline_label,
              pileup_bins, thresholds, *hist_opts):
        """ This is not in an init function for the case where we don't
        reload things from disk """
        self.online_label = online_label
        self.offline_label = offline_label
        self.pileup_bins = bn.Sorted(pileup_bins)
        self.thresholds = bn.GreaterThan(thresholds)
        self.hist_opts = hist_opts
        self.yields = hist.HistogramCollection(
                [self.pileup_bins, self.thresholds],
                "Hist1D", *hist_opts)
        test = self.yields.get_bin_contents([1,1])
        print("BEK:",test,type(test))

    def reload(self):
        """ Reload histograms from existing files on disk """
        pass

    def fill(self, pileup, online, offline):
        self.yields[pileup, online].fill(offline)

    def draw(self, with_fits=True):
        # Calclate the efficiency for each threshold
        test = self.yields.get_bin_contents([1,1])
        print("BEK:",test,type(test))
        self.__fill_turnons(with_fits)
        test = self.yields.get_bin_contents([1,1])
        print("BEK:",test,type(test))

        # Overlay the "all" pile-up bin for each threshold
        all_pileup_effs = self.turnons.get_bin_contents([bn.everything])
        # Really need a better way to do this
        hists = [hist for hist, key in all_pileup_effs.iteritems() 
                  if isinstance(key, int)]
        self.__make_overlay("all_thresholds", hists)
        
        # Overlay individual pile-up bins for each threshold

        # Produce the fit summary plot
        if with_fits:
            self.__summarize_fits()

    def __fill_turnons(self, with_fits):
        test = self.yields.get_bin_contents([1,1])
        print("BEK:",test,type(test))
        self.turnons = hist.HistogramCollection(
                [self.pileup_bins, self.thresholds],
                "Efficiency")
        test = self.yields.get_bin_contents([1,1])
        turn = self.turnons.get_bin_contents([1,1])
        test.check_compatibility(turn.histogram,True)
        print("BEK:",test,type(test))
        for pileup_bin in self.yields.iter_all():
            total = self.yields.get_bin_contents([pileup_bin, bn.Base.everything])
            for threshold_bin in self.yields.get_bin_contents([pileup_bin]):
                passed = self.yields.get_bin_contents([pileup_bin, threshold_bin])
                turnon = self.turnons.get_bin_contents([pileup_bin, threshold_bin])
                print("BEK:",passed, type(passed) )
                print("BEK:",total, type(total) )
                turnon.passed = passed
                turnon.total = total
                if with_fits:
                    __fit_one_turnon(turnon)

    def __make_overlay(self, file_kernel, hists):
        # Need a canvas
        canvas = Canvas()

        # Draw each turnon (with fit)
        draw(hists)

        # Add labels
        # Add a legend
        # Save canvas to file
        canvas.SaveAs(file_kernel)

    def __summarize_fits(self):
        pass



def __fit_one_turnon(turnon):
    pass
