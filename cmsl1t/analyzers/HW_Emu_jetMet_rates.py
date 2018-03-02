import numpy as np
import six
import ROOT
import os
from cmsl1t.analyzers.BaseAnalyzer import BaseAnalyzer
from cmsl1t.collections import HistogramsByPileUpCollection
from cmsl1t.utils.draw import draw, label_canvas
from cmsl1t.plotting.rates import RatesPlot
from cmsl1t.playground.lumifilters import lumiFilter
import cmsl1t.hist.binning as bn

def types():
    sum_types = ["HT", "METBE", "METHF"]
    jet_types = ["JetET"]
    sum_types += [t + '_Emu' for t in sum_types]
    jet_types += [t + '_Emu' for t in jet_types]

    return sum_types, jet_types

def extractSums(event):

    online = dict(
        HT=event.l1Sums["L1Htt"],
        METBE=event.l1Sums["L1Met"],
        METHF=event.l1Sums["L1MetHF"],
        HT_Emu=event.l1Sums["L1EmuHtt"],
        METBE_Emu=event.l1Sums["L1EmuMet"],
        METHF_Emu=event.l1Sums["L1EmuMetHF"],
     )

    return online


class Analyzer(BaseAnalyzer):

    def __init__(self, config, **kwargs):
        super(Analyzer, self).__init__("HW_Emu_jet_rates", config)
        self.triggerName = self.config.get('input', 'trigger')['name']

        self._lumiJson = config.try_get('input', 'lumi_json', '')
        self._lastLumi = -1
        self._processLumi = True
        self._sumTypes, self._jetTypes = types() 

        for name in self._sumTypes + self._jetTypes:
            rates_plot = RatesPlot(name)
            self.register_plotter(rates_plot)
            setattr(self, name + "_rates", rates_plot)

    def prepare_for_events(self, reader):
        bins = np.arange(0.0, 400.0, 1.0)
        puBins = self.puBins

        for name in self._sumTypes + self._jetTypes:
            rates_plot = getattr(self, name + "_rates")
            rates_plot.build(name, puBins, 400, 0, 400)

        '''
        self.rates = HistogramsByPileUpCollection(
            pileupBins=puBins, dimensions=2)
        for thing in object_types:
            self.rates.add(thing, bins)
        '''

        return True
    
    '''
    def reload_histograms(self, input_file):
        # Something like this needs to be implemented still
        self.rates = HistogramsByPileUpCollection.from_root(input_file)
        return True
    '''

    def fill_histograms(self, entry, event):

        if self._lumiJson:
            if event._lumi != self._lastLumi:
                self._lastLumi = event._lumi
                if lumiFilter(event._run, event._lumi, self._lumiJson):
                    self._processLumi = True
                else:
                    self._processLumi = False
                    return True

        if not self._processLumi:
            return True

        # Get pileup if ntuples have reco trees in them.
        # If not, set PU to 1 so that it fills the (only) pu bin.
        try:
            pileup = event.nVertex
        except AttributeError:
            pileup = 1.

        #Sums:
        online = extractSums(event)
        for name in self._sumTypes:
            on = online[name]
            getattr(self, name + "_rates").fill(pileup, on.et)

        #Jets:
        l1JetEts = [jet.et for jet in event._l1Jets]
        nJets = len(l1JetEts)
        if nJets > 0:
            maxL1JetEt = max(l1JetEts)
        else:
            maxL1JetEt = 0.


        l1EmuJetEts = [jet.et for jet in event._l1EmuJets]
        nEmuJets = len(l1EmuJetEts)
        if nEmuJets > 0:
            maxL1EmuJetEt = max(l1EmuJetEts)
        else:
            maxL1EmuJetEt = 0.


        for name in self._jetTypes:
            if 'Emu' in name:
                getattr(self, name + '_rates').fill(pileup, maxL1EmuJetEt)
            else:
                getattr(self, name + '_rates').fill(pileup, maxL1JetEt)

        return True

    def make_plots(self):

        # TODO: implement this in BaseAnalyzer
        # make_plots -> make_plots(plot_func)

        # Get EMU thresholds for each HW threshold.

        THRESHOLDS = self.thresholds
        if THRESHOLDS == None:
            print('Error: Please specify thresholds in the config .yaml in dictionary format')

        # calculate cumulative histograms
        for plot in self.all_plots:
            hist = plot.plots.get_bin_contents([bn.Base.everything])
            bin1 = hist.get_bin_content(1)
            if bin1 != 0.:
                hist.Scale(40000000./bin1)
            h = get_cumulative_hist(hist)
            bin1cumul = h.get_bin_content(1)
            if bin1cumul != 0.:
                h.Scale(40000000./bin1cumul)
            setattr(self, plot.online_name, h)
            plot.draw()

        print('  thresholds:')

        for histo_name in self._sumTypes + self._jetTypes:
            if "_Emu" in histo_name:
                continue
            h = getattr(self, histo_name)
            h_emu = getattr(self, histo_name + "_Emu")
            bin1 = h.get_bin_content(1)
            if bin1 != 0.:
                h.Scale(40000000./bin1)
            bin1_emu = h_emu.get_bin_content(1)
            if bin1_emu != 0.:
                h_emu.Scale(40000000./bin1_emu)
            thresholds = THRESHOLDS.get(histo_name)
            emu_thresholds = []
            for thresh in thresholds:
                rate_delta = []
                hw_rate = h.get_bin_content(thresh)
                for i in range(h.nbins()):
                    emu_rate = h_emu.get_bin_content(i)
                    if hw_rate == 0. or emu_rate == 0.:
                        rate_delta.append(40000000.)
                    else:
                        rate_delta.append(abs(hw_rate - emu_rate))
                emu_thresholds.append(rate_delta.index(min(rate_delta)))
            outputline = ('    {0}: {1}'.format(histo_name, thresholds) + '\n'
                          + '    {0}: {1}'.format(histo_name + '_Emu', emu_thresholds))
            print(outputline)

        '''
        for histo_name in object_types:
            h = getattr(self, histo_name)
            plot(h, histo_name, self.output_folder)
        '''
        return True


def _reverse(a):
    return np.array(np.flipud(a))


def get_cumulative_hist(hist):
    h = hist.clone(hist.name + '_cumul')
    arr = np.cumsum(_reverse([bin.value for bin in hist]))
    h.set_content(_reverse(arr))
    errors_sq = np.cumsum(_reverse([bin.error**2 for bin in hist]))
    h.set_error(_reverse(np.sqrt(errors_sq)))

    # now scale
    bin1 = h.get_bin_content(1)
    if bin1 != 0:
        h.GetSumw2()
        h.Scale(4.0e7 / bin1)
    return h


def plot(hist, name, output_folder):
    pu = ''
    if '_pu' in name:
        pu = name.split('_')[-1]
        name = name.replace('_' + pu, '')
    file_name = 'rates_{name}'.format(name=name)
    if 'nVertex' in name:
        file_name = 'nVertex'
    if pu:
        file_name += '_' + pu
    canvas_name = file_name.replace('SingleMu', 'Rates')
    c = ROOT.TCanvas(canvas_name)
    if 'nVertex' not in name:
        c.SetLogy()
    hist.set_y_title('Rate (Hz)')
    hist.set_x_title(name)
    hist.Draw()
    c.SaveAs(os.path.join(output_folder, file_name + '.pdf'))
