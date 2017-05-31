import bisect
from exceptions import KeyError
from copy import deepcopy
import logging


logger = logging.getLogger(__name__)


class Base():
    overflow = "overflow"
    underflow = "underflow"

    def __init__(self, label):
        self.label = label

    def set_contained_obj(self, contains):
        self.values = {}
        for i in range(self.n_bins) + [self.overflow, self.underflow]:
            self.values[i] = deepcopy(contains)

    def __len__(self):
        return self.n_bins

    def get_bin_contents(self, bin_index):
        contents = self.values.get(bin_index, None)
        if contents is None:
            msg = "Cannot find bin for index, {0}, for binning called '{1}'"
            logger.error(msg.format(bin_index, self.label))
            raise KeyError(bin_index)
        return contents

    def __getitem__(self, value):
        bins = self.find_bins(value)
        return [self.get_bin_contents(i) for i in bins]

    def __iter__(self):
        for i in range(self.n_bins):
            yield i


class Sorted(Base):
    import bisect

    def __init__(self, bin_edges, label=None):
        Base.__init__(self, label)
        self.bins = sorted(bin_edges)
        self.n_bins = len(self.bins)

    def find_bins(self, value):
        if value < self.bins[0]:
            found_bin = self.underflow
        elif value >= self.bins[-1]:
            found_bin = self.overflow
        else:
            found_bin = bisect.bisect(self.bins, value) - 1
        return [found_bin]


class GreaterThan(Base):
    def __init__(self, bins, label=None):
        Base.__init__(self, label)
        self.bins = bins
        self.n_bins = len(self.bins)

    def find_bins(self, value):
        contained_in = []
        for i, threshold in enumerate(self.bins):
            if value >= threshold:
                contained_in.append(i)
        if len(contained_in) == 0:
            contained_in = [self.overflow]
        return contained_in


class Overlapped(Base):
    def __init__(self, bins, label=None):
        Base.__init__(self, label)
        self.bins = bins
        self.n_bins = len(self.bins)

    def find_bins(self, value):
        contained_in = []
        for i, (bin_low, bin_high) in enumerate(self.bins):
            if value >= bin_low and value < bin_high:
                contained_in.append(i)
        if len(contained_in) == 0:
            contained_in = [self.overflow]
        return contained_in


class EtaRegions(Base):
    from cmsl1t.geometry import eta_regions

    def __init__(self, label=None):
        Base.__init__(self, label)
        self.n_bins = len(self.eta_regions)

    def find_bins(self, value):
        regions = []
        for region, is_contained in self.eta_regions.iteritems():
            if is_contained(value):
                regions.append(region)
        return regions


class WithAll(Base):
    def __init__(self, bins, label=None):
        Base.__init__(self, label)
        self.bins = bins
        self.n_bins = len(self.bins)

    def find_bins(self, value):
        contained_in = []
        for i, (bin_low, bin_high) in enumerate(self.bins):
            if value >= bin_low and value < bin_high:
                contained_in.append(i)
        if len(contained_in) == 0:
            contained_in = [self.overflow]
        return contained_in
