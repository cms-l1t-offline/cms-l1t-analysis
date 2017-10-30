"""
Make plots for offline met studies
"""

from BaseAnalyzer import BaseAnalyzer
from cmsl1t.plotting.efficiency import EfficiencyPlot
from cmsl1t.collections import EfficiencyCollection
from cmsl1t.plotting.onlineVsOffline import OnlineVsOffline
from cmsl1t.plotting.resolution import ResolutionPlot
from cmsl1t.plotting.resolution_vs_X import ResolutionVsXPlot
import cmsl1t.recalc.met as recalc
from cmsl1t.playground.eventreader import Met, Sum
from math import pi
import pprint
from collections import namedtuple
import numpy as np


sum_types = ["HTT", "HTT_Emu", "MHT", "MET_HF", "MET", "MET_PF", "MET_PF_NoMu", "MET_PF_HF", "MET_PF_NoMu_HF",
              "MHT_Emu", "MET_HF_Emu", "MET_Emu", "MET_PF_Emu", "MET_PF_NoMu_Emu", "MET_PF_HF_Emu", "MET_PF_NoMu_HF_Emu"]
jet_types = ["jetET_B", "jetET_E", "jetET_BE", "jetET_HF", "jetET_B_Emu", "jetET_E_Emu", "jetET_BE_Emu", "jetET_HF_Emu"]
Sums = namedtuple("Sums", sum_types)


def ExtractSums(event):
    offline = dict(HTT=Sum(event.sums.Ht),
                   MHT=Met(event.sums.mHt, event.sums.mHtPhi),
                   MET_HF=Met(event.sums.caloMet, event.sums.caloMetPhi),
                   MET=Met(event.sums.caloMetBE, event.sums.caloMetPhiBE),
                   MET_PF=Met(event.sums.met, event.sums.metPhi),
                   MET_PF_NoMu=Met(event.sums.pfMetNoMu, event.sums.pfMetNoMuPhi),
                   MET_PF_HF=Met(event.sums.met, event.sums.metPhi),
                   MET_PF_NoMu_HF=Met(event.sums.pfMetNoMu, event.sums.pfMetNoMuPhi),
                   HTT_Emu=Sum(event.sums.Ht),
                   MHT_Emu=Met(event.sums.mHt, event.sums.mHtPhi),
                   MET_HF_Emu=Met(event.sums.caloMet, event.sums.caloMetPhi),
                   MET_Emu=Met(event.sums.caloMetBE, event.sums.caloMetPhiBE),
                   MET_PF_Emu=Met(event.sums.met, event.sums.metPhi),
                   MET_PF_NoMu_Emu=Met(event.sums.pfMetNoMu, event.sums.pfMetNoMuPhi),
                   MET_PF_HF_Emu=Met(event.sums.met, event.sums.metPhi),
                   MET_PF_NoMu_HF_Emu=Met(event.sums.pfMetNoMu, event.sums.pfMetNoMuPhi)
                   )
    online = dict(HTT=event.l1Sums["L1Htt"],
                  MHT=event.l1Sums["L1Mht"],
                  MET_HF=event.l1Sums["L1MetHF"],
                  MET=event.l1Sums["L1Met"],
                  MET_PF=event.l1Sums["L1Met"],
                  MET_PF_NoMu=event.l1Sums["L1Met"],
                  MET_PF_HF=event.l1Sums["L1MetHF"],
                  MET_PF_NoMu_HF=event.l1Sums["L1MetHF"],
                  HTT_Emu=event.l1Sums["L1EmuHtt"],
                  MHT_Emu=event.l1Sums["L1EmuMht"],
                  MET_HF_Emu=event.l1Sums["L1EmuMetHF"],
                  MET_Emu=event.l1Sums["L1EmuMet"],
                  MET_PF_Emu=event.l1Sums["L1EmuMet"],
                  MET_PF_NoMu_Emu=event.l1Sums["L1EmuMet"],
                  MET_PF_HF_Emu=event.l1Sums["L1EmuMetHF"],
                  MET_PF_NoMu_HF_Emu=event.l1Sums["L1EmuMetHF"]
                  )
    return online, offline


class Analyzer(BaseAnalyzer):
    def __init__(self, config, **kwargs):
        super(Analyzer, self).__init__("offline_met_analyzer", config)

        for name in sum_types:
            eff_plot = EfficiencyPlot("L1", "offline_" + name)
            res_plot = ResolutionPlot("energy", "L1", "offline_" + name)
            twoD_plot = OnlineVsOffline("L1", "offline_" + name)
            self.register_plotter(eff_plot)
            self.register_plotter(res_plot)
            self.register_plotter(twoD_plot)
            setattr(self, name + "_eff", eff_plot)
            setattr(self, name + "_res", res_plot)
            setattr(self, name + "_2D", twoD_plot)

            eff_plot_HR = EfficiencyPlot("L1", "offline_" + name + "_HiRange")
            twoD_plot_HR = OnlineVsOffline("L1", "offline_" + name + "_HiRange")
            self.register_plotter(eff_plot_HR)
            self.register_plotter(twoD_plot_HR)
            setattr(self, name + "_eff_HR", eff_plot_HR)
            setattr(self, name + "_2D_HR", twoD_plot_HR)

        for angle in sum_types[2:]:
            name = angle + "_phi"
            res_plot = ResolutionPlot("phi", "L1", "offline_" + name)
            twoD_plot = OnlineVsOffline("L1", "offline_" + name)
            self.register_plotter(res_plot)
            self.register_plotter(twoD_plot)
            setattr(self, name + "_res", res_plot)
            setattr(self, name + "_2D", twoD_plot)

        for name in jet_types:
            eff_plot = EfficiencyPlot("L1", "offline_" + name)
            res_plot = ResolutionPlot("energy", "L1", "offline_" + name)
            twoD_plot = OnlineVsOffline("L1", "offline_" + name)
            self.register_plotter(eff_plot)
            self.register_plotter(res_plot)
            self.register_plotter(twoD_plot)
            setattr(self, name + "_eff", eff_plot)
            setattr(self, name + "_res", res_plot)
            setattr(self, name + "_2D", twoD_plot)

            eff_plot_HR = EfficiencyPlot("L1", "offline_" + name + "_HiRange")
            twoD_plot_HR = OnlineVsOffline("L1", "offline_" + name + "_HiRange")
            self.register_plotter(eff_plot_HR)
            self.register_plotter(twoD_plot_HR)
            setattr(self, name + "_eff_HR", eff_plot_HR)
            setattr(self, name + "_2D_HR", twoD_plot_HR)

        self.res_vs_eta_CentralJets = ResolutionVsXPlot("energy", "onlineJet", "offlineJet", "offlineJet_eta")
        self.register_plotter(self.res_vs_eta_CentralJets)

    def prepare_for_events(self, reader, puBins=[0,10,20,30,40,999]):
        # TODO: Get these from a common place, and / or the config file
        #puBins = range(0, 50, 10) + [999]
        puBins_HR = [0, 999]
        tmpbins0 = range(0, 100, 5)
        tmpbins1 = range(100, 400, 10)
        tmpbins2 = range(400, 800, 50)
        tmpbins3 = range(800, 1000, 200)
        tmpbins4 = range(1000, 2100, 500)
        tmpbins0.extend(tmpbins1)
        tmpbins0.extend(tmpbins2)
        tmpbins0.extend(tmpbins3)
        tmpbins0.extend(tmpbins4)
        xbins = np.asarray(tmpbins0, 'd')    #The 'd' arg is vital here, else it will claim axis length zero...

        # Eta ranges so we can put |\eta| < val as the legend header on the efficiency plots.
        eta_ranges = dict(HTT="|\\eta| < 2.5",
                  MHT="|\\eta| < 2.5",
                  MET_HF="|\\eta| < 5.0",
                  MET="|\\eta| < 3.0",
                  MET_PF="|\\eta| < 3.0",
                  MET_PF_NoMu="|\\eta| < 3.0",
                  MET_PF_HF="|\\eta| < 5.0",
                  MET_PF_NoMu_HF="|\\eta| < 5.0",
                  jetET_B="|\\eta| < 1.479",
                  jetET_E="1.479 < |\\eta| < 3.0",
                  jetET_BE="|\\eta| < 3.0",
                  jetET_HF="3.0 < |\\eta| < 5.0",
                  HTT_Emu="|\\eta| < 2.5",
                  MHT_Emu="|\\eta| < 2.5",
                  MET_HF_Emu="|\\eta| < 5.0",
                  MET_Emu="|\\eta| < 3.0",
                  MET_PF_Emu="|\\eta| < 3.0",
                  MET_PF_NoMu_Emu="|\\eta| < 3.0",
                  MET_PF_HF_Emu="|\\eta| < 5.0",
                  MET_PF_NoMu_HF_Emu="|\\eta| < 5.0",
                  jetET_B_Emu="|\\eta| < 1.479",
                  jetET_E_Emu="1.479 < |\\eta| < 3.0",
                  jetET_BE_Emu="|\\eta| < 3.0",
                  jetET_HF_Emu="3.0 < |\\eta| < 5.0"
                  )

        thresholds = dict(HTT=[160, 220, 280, 340, 400],
                  MHT=[40, 60, 80, 100, 120],
                  MET_HF=[40, 60, 80, 100, 120],
                  MET=[40, 60, 80, 100, 120],
                  MET_PF=[40, 60, 80, 100, 120],
                  MET_PF_NoMu=[40, 60, 80, 100, 120],
                  MET_PF_HF=[40, 60, 80, 100, 120],
                  MET_PF_NoMu_HF=[40, 60, 80, 100, 120],
                  jetET_B=[35, 60, 90, 140, 180],
                  jetET_E=[35, 60, 90, 140, 180],
                  jetET_BE=[35, 60, 90, 140, 180],
                  jetET_HF=[35, 60, 90, 140, 180],
                  HTT_Emu=[160, 220, 280, 340, 400],
                  MHT_Emu=[40, 60, 80, 100, 120],
                  MET_HF_Emu=[40, 60, 80, 100, 120],
                  MET_Emu=[40, 60, 80, 100, 120],
                  MET_PF_Emu=[40, 60, 80, 100, 120],
                  MET_PF_NoMu_Emu=[40, 60, 80, 100, 120],
                  MET_PF_HF_Emu=[40, 60, 80, 100, 120],
                  MET_PF_NoMu_HF_Emu=[40, 60, 80, 100, 120],
                  jetET_B_Emu=[35, 60, 90, 140, 180],
                  jetET_E_Emu=[35, 60, 90, 140, 180],
                  jetET_BE_Emu=[35, 60, 90, 140, 180],
                  jetET_HF_Emu=[35, 60, 90, 140, 180]
                  )

        Config = namedtuple("Config", "name off_title on_title min off_max on_max")
        HTT_cfg = Config("HTT", "Offline HTT", "L1 HTT", 30, 600, 600)
        MHT_cfg = Config("MHT", "Offline MHT", "L1 MHT", 0, 400, 400)
        MET_HF_cfg = Config("MET_HF", "Offline MET with HF", "L1 MET", 0, 400, 400)
        MET_cfg = Config("MET", "Offline MET no HF", "L1 MET", 0, 400, 400)
        MET_PF_cfg = Config("MET_PF", "Offline PF MET", "L1 MET", 0, 400, 400)
        MET_PF_NoMu_cfg = Config("MET_PF_NoMu", "Offline PF MET without Muons", "L1 MET", 0, 400, 400)
        MET_PF_HF_cfg = Config("MET_PF_HF", "Offline PF MET with HF", "L1 MET", 0, 400, 400)
        MET_PF_NoMu_HF_cfg = Config("MET_PF_NoMu_HF", "Offline PF MET with HF without Muons", "L1 MET", 0, 400, 400)
        HTT_cfg_HR = Config("HTT", "Offline HTT", "L1 HTT", 30, 2000, 2000)
        MHT_cfg_HR = Config("MHT", "Offline MHT", "L1 MHT", 0, 2000, 2000)
        MET_HF_cfg_HR = Config("MET_HF", "Offline MET with HF", "L1 MET", 0, 2000, 2000)
        MET_cfg_HR = Config("MET", "Offline MET no HF", "L1 MET", 0, 2000, 2000)
        MET_PF_cfg_HR = Config("MET_PF", "Offline PF MET", "L1 MET", 0, 2000, 2000)
        MET_PF_NoMu_cfg_HR = Config("MET_PF_NoMu", "Offline PF MET without Muons", "L1 MET", 0, 2000, 2000)
        MET_PF_HF_cfg_HR = Config("MET_PF_HF", "Offline PF MET with HF", "L1 MET", 0, 2000, 2000)
        MET_PF_NoMu_HF_cfg_HR = Config("MET_PF_NoMu_HF", "Offline PF MET with HF without Muons", "L1 MET", 0, 2000, 2000)

        HTT_Emu_cfg = Config("HTT_Emu", "Offline HTT", "L1 HTT", 30, 600, 600)
        MHT_Emu_cfg = Config("MHT_Emu", "Offline MHT", "L1 MHT", 0, 400, 400)
        MET_HF_Emu_cfg = Config("MET_HF_Emu", "Offline MET with HF", "L1 MET", 0, 400, 400)
        MET_Emu_cfg = Config("MET_Emu", "Offline MET no HF", "L1 MET", 0, 400, 400)
        MET_PF_Emu_cfg = Config("MET_PF_Emu", "Offline PF MET", "L1 MET", 0, 400, 400)
        MET_PF_NoMu_Emu_cfg = Config("MET_PF_NoMu_Emu", "Offline PF MET without Muons", "L1 MET", 0, 400, 400)
        MET_PF_HF_Emu_cfg = Config("MET_PF_HF_Emu", "Offline PF MET with HF", "L1 MET", 0, 400, 400)
        MET_PF_NoMu_HF_Emu_cfg = Config("MET_PF_NoMu_HF_Emu", "Offline PF MET with HF without Muons", "L1 MET", 0, 400, 400)
        HTT_Emu_cfg_HR = Config("HTT_Emu", "Offline HTT", "L1 HTT", 30, 2000, 2000)
        MHT_Emu_cfg_HR = Config("MHT_Emu", "Offline MHT", "L1 MHT", 0, 2000, 2000)
        MET_HF_Emu_cfg_HR = Config("MET_HF_Emu", "Offline MET with HF", "L1 MET", 0, 2000, 2000)
        MET_Emu_cfg_HR = Config("MET_Emu", "Offline MET no HF", "L1 MET", 0, 2000, 2000)
        MET_PF_Emu_cfg_HR = Config("MET_PF_Emu", "Offline PF MET", "L1 MET", 0, 2000, 2000)
        MET_PF_NoMu_Emu_cfg_HR = Config("MET_PF_NoMu_Emu", "Offline PF MET without Muons", "L1 MET", 0, 2000, 2000)
        MET_PF_HF_Emu_cfg_HR = Config("MET_PF_HF_Emu", "Offline PF MET with HF", "L1 MET", 0, 2000, 2000)
        MET_PF_NoMu_HF_Emu_cfg_HR = Config("MET_PF_NoMu_HF_Emu", "Offline PF MET with HF without Muons", "L1 MET", 0, 2000, 2000)

        jetET_Barrel_cfg = Config("jetET_B", "Offline Jet ET in Barrel Region", "L1 Jet ET", 0, 400, 400)
        jetET_Endcap_cfg = Config("jetET_E", "Offline Jet ET in Barrel Region", "L1 Jet ET", 0, 400, 400)
        jetET_Central_cfg = Config("jetET_BE", "Offline Jet ET in Central Region", "L1 Jet ET", 0, 400, 400)
        jetET_HF_cfg = Config("jetET_HF", "Offline Jet ET in HF Region", "L1 Jet ET", 0, 400, 400)
        jetET_Barrel_cfg_HR = Config("jetET_B", "Offline Jet ET in Barrel Region", "L1 Jet ET", 0, 2000, 2000)
        jetET_Endcap_cfg_HR = Config("jetET_E", "Offline Jet ET in Barrel Region", "L1 Jet ET", 0, 2000, 2000)
        jetET_Central_cfg_HR = Config("jetET_BE", "Offline Jet ET in Central Region", "L1 Jet ET", 0, 2000, 2000)
        jetET_HF_cfg_HR = Config("jetET_HF", "Offline Jet ET in HF Region", "L1 Jet ET", 0, 2000, 2000)

        jetET_Barrel_Emu_cfg = Config("jetET_B_Emu", "Offline Jet ET in Barrel Region", "L1 Jet ET", 0, 400, 400)
        jetET_Endcap_Emu_cfg = Config("jetET_E_Emu", "Offline Jet ET in Barrel Region", "L1 Jet ET", 0, 400, 400)
        jetET_Central_Emu_cfg = Config("jetET_BE_Emu", "Offline Jet ET in Central Region", "L1 Jet ET", 0, 400, 400)
        jetET_HF_Emu_cfg = Config("jetET_HF_Emu", "Offline Jet ET in HF Region", "L1 Jet ET", 0, 400, 400)
        jetET_Barrel_Emu_cfg_HR = Config("jetET_B_Emu", "Offline Jet ET in Barrel Region", "L1 Jet ET", 0, 2000, 2000)
        jetET_Endcap_Emu_cfg_HR = Config("jetET_E_Emu", "Offline Jet ET in Barrel Region", "L1 Jet ET", 0, 2000, 2000)
        jetET_Central_Emu_cfg_HR = Config("jetET_BE_Emu", "Offline Jet ET in Central Region", "L1 Jet ET", 0, 2000, 2000)
        jetET_HF_Emu_cfg_HR = Config("jetET_HF_Emu", "Offline Jet ET in HF Region", "L1 Jet ET", 0, 2000, 2000)

        

        cfgs = [HTT_cfg, MHT_cfg, MET_HF_cfg, MET_cfg, MET_PF_cfg, MET_PF_NoMu_cfg, MET_PF_HF_cfg, MET_PF_NoMu_HF_cfg,
                  jetET_Barrel_cfg, jetET_Endcap_cfg, jetET_Central_cfg, jetET_HF_cfg,
                  HTT_Emu_cfg, MHT_Emu_cfg, MET_HF_Emu_cfg, MET_Emu_cfg, MET_PF_Emu_cfg, MET_PF_NoMu_Emu_cfg, MET_PF_HF_Emu_cfg, MET_PF_NoMu_HF_Emu_cfg,
                  jetET_Barrel_Emu_cfg, jetET_Endcap_Emu_cfg, jetET_Central_Emu_cfg, jetET_HF_Emu_cfg,]

        cfgs2 = [HTT_cfg_HR, MHT_cfg_HR, MET_HF_cfg_HR, MET_cfg_HR, MET_PF_cfg_HR, MET_PF_NoMu_cfg_HR, MET_PF_HF_cfg_HR, MET_PF_NoMu_HF_cfg_HR,
                  jetET_Barrel_cfg_HR, jetET_Endcap_cfg_HR, jetET_Central_cfg_HR, jetET_HF_cfg_HR,
                  HTT_Emu_cfg_HR, MHT_Emu_cfg_HR, MET_HF_Emu_cfg_HR, MET_Emu_cfg_HR, MET_PF_Emu_cfg_HR, MET_PF_NoMu_Emu_cfg_HR, MET_PF_HF_Emu_cfg_HR, MET_PF_NoMu_HF_Emu_cfg_HR,
                  jetET_Barrel_Emu_cfg_HR, jetET_Endcap_Emu_cfg_HR, jetET_Central_Emu_cfg_HR, jetET_HF_Emu_cfg_HR]

        for cfg in cfgs:
            eff_plot = getattr(self, cfg.name + "_eff")
            res_plot = getattr(self, cfg.name + "_res")
            twoD_plot = getattr(self, cfg.name + "_2D")
            eff_plot.build(cfg.on_title, cfg.off_title + " (GeV)",
                           puBins, thresholds.get(cfg.name), 50, cfg.min, cfg.off_max, legend_title=eta_ranges.get(cfg.name, ""))
            twoD_plot.build(cfg.on_title, cfg.off_title + " (GeV)",
                            puBins, 50, cfg.min, cfg.off_max)
            res_plot.build(cfg.on_title, cfg.off_title,
                           puBins, 50, -10, 10)

            if not hasattr(self, cfg.name + "_phi_res"):
                continue
            res_plot = getattr(self, cfg.name + "_phi_res")
            twoD_plot = getattr(self, cfg.name + "_phi_2D")
            twoD_plot.build(cfg.on_title + " Phi (rad)", cfg.off_title + " Phi (rad)",
                            puBins, 50, -pi, 2 * pi)
            res_plot.build(cfg.on_title + " Phi", cfg.off_title + " Phi",
                           puBins, 50, -2, 2)

        for cfg in cfgs2:
            eff_plot_HR = getattr(self, cfg.name + "_eff_HR")
            twoD_plot_HR = getattr(self, cfg.name + "_2D_HR")
            eff_plot_HR.build(cfg.on_title, cfg.off_title + " (GeV)",
                           puBins_HR, thresholds.get(cfg.name), xbins.size - 1, xbins, legend_title=eta_ranges.get(cfg.name, ""))
            twoD_plot_HR.build(cfg.on_title, cfg.off_title + " (GeV)",
                            puBins_HR, xbins.size - 1, xbins)

        self.res_vs_eta_CentralJets.build("Online Jet energy (GeV)",
                                          "Offline Jet energy (GeV)", "Offline Jet Eta (rad)",
                                          puBins, 50, -0.5, 3.5, 50, -5.0, 5.0)
        return True

    def fill_histograms(self, entry, event):
        if not event.passesMETFilter():
            return True

        offline, online = ExtractSums(event)
        pileup = event.nVertex

        for name in sum_types:
            on = online[name]
            if on.et == 0:
                continue
            off = offline[name]
            getattr(self, name + "_eff").fill(pileup, off.et, on.et)
            getattr(self, name + "_res").fill(pileup, off.et, on.et)
            getattr(self, name + "_2D").fill(pileup, off.et, on.et)
            getattr(self, name + "_eff_HR").fill(pileup, off.et, on.et)
            getattr(self, name + "_2D_HR").fill(pileup, off.et, on.et)
            if hasattr(self, name + "_phi_res"):
                getattr(self, name + "_phi_res").fill(pileup, off.phi, on.phi)
                getattr(self, name + "_phi_2D").fill(pileup, off.phi, on.phi)

        goodJets = event.goodJets()

        for recoJet in event.goodJets():
            l1Jet = event.getMatchedL1Jet(recoJet, l1Type='EMU')
            if not l1Jet:
                continue
            if recoJet.etCorr > 30.:
                self.res_vs_eta_CentralJets.fill(pileup, recoJet.eta, recoJet.etCorr, l1Jet.et)

        leadingRecoJet = event.getLeadingRecoJet()
        if not leadingRecoJet:
            return True

        l1EmuJet = event.getMatchedL1Jet(leadingRecoJet, l1Type='EMU')
        if not l1EmuJet:
            return True

        if abs(leadingRecoJet.eta) < 1.479:
            getattr(self, "jetET_B_Emu_eff").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)
            getattr(self, "jetET_B_Emu_res").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)
            getattr(self, "jetET_B_Emu_2D").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)
            getattr(self, "jetET_B_Emu_eff_HR").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)
            getattr(self, "jetET_B_Emu_2D_HR").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)

            getattr(self, "jetET_BE_Emu_eff").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)
            getattr(self, "jetET_BE_Emu_res").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)
            getattr(self, "jetET_BE_Emu_2D").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)
            getattr(self, "jetET_BE_Emu_eff_HR").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)
            getattr(self, "jetET_BE_Emu_2D_HR").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)

        elif abs(leadingRecoJet.eta) < 3.0:
            getattr(self, "jetET_E_Emu_eff").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)
            getattr(self, "jetET_E_Emu_res").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)
            getattr(self, "jetET_E_Emu_2D").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)
            getattr(self, "jetET_E_Emu_eff_HR").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)
            getattr(self, "jetET_E_Emu_2D_HR").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)

            getattr(self, "jetET_BE_Emu_eff").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)
            getattr(self, "jetET_BE_Emu_res").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)
            getattr(self, "jetET_BE_Emu_2D").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)
            getattr(self, "jetET_BE_Emu_eff_HR").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)
            getattr(self, "jetET_BE_Emu_2D_HR").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)

        else:
            getattr(self, "jetET_HF_Emu_eff").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)
            getattr(self, "jetET_HF_Emu_res").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)
            getattr(self, "jetET_HF_Emu_2D").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)
            getattr(self, "jetET_HF_Emu_eff_HR").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)
            getattr(self, "jetET_HF_Emu_2D_HR").fill(pileup, leadingRecoJet.etCorr, l1EmuJet.et)

        l1Jet = event.getMatchedL1Jet(leadingRecoJet, l1Type='HW')
        if not l1Jet:
            return True

        if abs(leadingRecoJet.eta) < 1.479:
            getattr(self, "jetET_B_eff").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)
            getattr(self, "jetET_B_res").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)
            getattr(self, "jetET_B_2D").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)
            getattr(self, "jetET_B_eff_HR").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)
            getattr(self, "jetET_B_2D_HR").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)

            getattr(self, "jetET_BE_eff").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)
            getattr(self, "jetET_BE_res").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)
            getattr(self, "jetET_BE_2D").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)
            getattr(self, "jetET_BE_eff_HR").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)
            getattr(self, "jetET_BE_2D_HR").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)

        elif abs(leadingRecoJet.eta) < 3.0:
            getattr(self, "jetET_E_eff").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)
            getattr(self, "jetET_E_res").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)
            getattr(self, "jetET_E_2D").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)
            getattr(self, "jetET_E_eff_HR").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)
            getattr(self, "jetET_E_2D_HR").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)

            getattr(self, "jetET_BE_eff").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)
            getattr(self, "jetET_BE_res").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)
            getattr(self, "jetET_BE_2D").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)
            getattr(self, "jetET_BE_eff_HR").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)
            getattr(self, "jetET_BE_2D_HR").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)

        else:
            getattr(self, "jetET_HF_eff").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)
            getattr(self, "jetET_HF_res").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)
            getattr(self, "jetET_HF_2D").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)
            getattr(self, "jetET_HF_eff_HR").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)
            getattr(self, "jetET_HF_2D_HR").fill(pileup, leadingRecoJet.etCorr, l1Jet.et)

        return True
