import bisect
from exceptions import KeyError
from copy import deepcopy
import logging


logger = logging.getLogger(__name__)


class Base():
    overflow = "overflow"
    underflow = "underflow"
    everything = "everything"

    def __init__(self, label, n_bins):
        self.label = label
        self.n_bins = n_bins
        self.values = { i:None for i in range(self.n_bins) }
        for i in [self.overflow, self.underflow, self.everything]:
            self.values[i]=None

    def set_all_values(self, value):
        for i in range(self.n_bins):
            self.values[i] = deepcopy(value)
        for i in [self.overflow, self.underflow, self.everything]:
            self.values[i] = deepcopy(value)

    def set_value(self,bin, value):
        self.values[bin] = value

    def __len__(self):
        return self.n_bins

    def get_bin_contents(self, bin_index):
        contents = self.values.get(bin_index, "DoesntExist")
        if contents is "DoesntExist":
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

    def iter_all(self):
        for i in self.values:
            yield i


class Sorted(Base):
    import bisect

    def __init__(self, bin_edges, label=None):
        Base.__init__(self, label, len(bin_edges))
        self.bins = sorted(bin_edges)

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
        Base.__init__(self, label, len(bins))
        self.bins = bins

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
        Base.__init__(self, label, len(bins))
        self.bins = bins

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
        Base.__init__(self, label, len(self.eta_regions))

    def find_bins(self, value):
        regions = []
        for region, is_contained in self.eta_regions.iteritems():
            if is_contained(value):
                regions.append(region)
        return regions
