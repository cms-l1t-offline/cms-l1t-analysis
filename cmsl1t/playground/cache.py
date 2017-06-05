class _CachedItem(object):

    def __init__(self, tree, index):
        self._tree = tree
        self._index = index

    def __getattr__(self, attr):
        return getattr(self._tree, attr)[self._index]


class CachedIndexedTree(object):
    '''
        Decorator object
    '''

    def __init__(self, tree, indexName):
        self._tree = tree
        self._cache = {}
        self._indexName = indexName

    def __getitem__(self, index):
        if index not in self._cache:
            self._cache[index] = _CachedItem(self._tree, index)
        return self._cache[index]

    def __getattr__(self, attr):
        return getattr(self._tree, attr)

    def __iter__(self):
        indices = getattr(self._tree, self._indexName)
        for i in range(indices):
            item = self.__getitem__(i)
            yield item

    def __len__(self):
        indices = getattr(self._tree, self._indexName)
        return indices
