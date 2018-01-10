import cmsl1t.geometry as geo


def pfMetFilter(event):

    reject_if = [
        not event._metFilterReco.MetFilters.hbheNoiseFilter,
        not event._metFilterReco.MetFilters.hbheNoiseIsoFilter,
        not event._metFilterReco.MetFilters.globalSuperTightHalo2016Filter,
        not event._metFilterReco.MetFilters.ecalDeadCellTPFilter,
        not event._metFilterReco.MetFilters.goodVerticesFilter,
        not event._metFilterReco.MetFilters.eeBadScFilter,
        not event._metFilterReco.MetFilters.badPFMuonFilter,
        not event._metFilterReco.MetFilters.badChCandFilter
    ]
    if any(reject_if):
        return False
    return True
