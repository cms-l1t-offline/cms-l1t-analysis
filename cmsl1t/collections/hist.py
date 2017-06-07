import collections


class HistogramCollection(object):
    '''
    The histogram collection needs a few things:
     - it needs to be able to essentially have binned maps of histograms
     - needs to know how to create new histograms

    e.g.
    def getter_pileup(value, bins)
            if pileup > max(bins):
                return -1
            bins = pairwise(bins)
            for i, (lowerEdge, upperEdge) in enumerate(bins):
                if pileup >= lowerEdge and pileup < upperEdge:
                    return i
            return 0

    def getter_region(eta, bins):
        for region in regions:
            if is_in_region(region, eta, regions=regions):
                return region


    def hist1D_factory(name, bins):
        pass


    hists = HistogramCollection(dimensions=2) #dimension 0 == histogram names?
    hists.register_dim(1, getter_pileup, bins=[0, 10, 20, 30, 999])
    hists.register_dim(2, getter_region, ['B', 'BE', 'E', 'HF'])
    '''

    def __init__(self, dimensions):
        '''
            Should dimensions include or exclude histogram names?
        '''
        self._dimensions = dimensions

    def register_dim(self, dim_index, segmentation_func, bins):
        '''
            Does it make sense to include bins here or is it better to use
            functools.partial and expect the segmentation_func to only handle 1
            parameter? Unless we pass a setter, we need the bins to add histograms
        '''
        pass

    def __getitem__(self, key):
        '''
            Supposed to handle
                coll[x]
            and
                coll[x, y, z]
        '''
        if isinstance(key, collections.Sequence) and not isinstance(obj, basestring):
            pass
        else:
            '''
                This bit also needs to support
                    coll[x][y][z]
            '''
            pass

    def __setitem__(self, key, value):
        '''
            Same requirements as __getitem__
        '''
        pass

    def add(self, name, bins):
        '''
            coll.add('1Dhistogram', bins=[1,2,3])
            coll.add('2Dhistogram', bins=[[1,2,3], [1,2,3]])
            coll.add('3Dhistogram', bins=[[1,2,3], [1,2,3], [1,2,3]])
        '''
        # get the segmentation of the current dimensions
        # create a histogram for each segment
        pass

    def fill(self, x, weight):
        '''
            Do we want this? It could only work if we have setters for each
            dimension:
                coll.set_dim(1, pileup)
                coll.set_dim(2, region)


                coll.fill('1Dhistogram', x=42, w=1)
                coll.fill('2Dhistogram', x=[42, 1], w=1)

            alternative is
                coll[pileup][eta][histname].fill(...)
        '''
        pass

    def __len__(self):
        return 0
