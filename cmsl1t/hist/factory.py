from cmsl1t.hist import BaseHistogram
import logging
import rootpy.plotting.hist as rootpy_hists
import rootpy.ROOT as ROOT
from exceptions import RuntimeError


logger = logging.getLogger(__name__)


class HistFactory():

    def __init__(self, hist_type, *vargs, **kwargs):
        self.hist_type = hist_type
        self.vargs = vargs
        self.kwargs = kwargs

        self.can_build = True
        self._prepare_hist_class()

    def _prepare_hist_class(self):
        histograms = []
        for hist in BaseHistogram.__subclasses__():
            if hist.__name__ == self.hist_type:
                histograms.append(hist)
        if hasattr(rootpy_hists, self.hist_type):
            histograms.append(getattr(rootpy_hists, self.hist_type))
        elif hasattr(ROOT, self.hist_type):
            histograms.append(getattr(ROOT, self.hist_type))
        if len(histograms) == 0:
            msg = "No valid histogram type called: '{0}'"
            msg = msg.format(self.hist_type)
            logger.error(msg)
            self.can_build = msg
            return
        elif len(histograms) > 1:
            msg = "Multiple histogram types are called: '{0}'"
            msg = msg.format(self.hist_type)
            logger.error(msg)
            self.can_build = msg
            return

        self.hist_class = histograms[0]

    def build(self, *vargs, **kwargs):
        if self.can_build is not True:
            raise RuntimeError(self.can_build)

        if len(kwargs) > 0:
            for attr in ["title", "name"]:
                if attr in self.kwargs:
                    new_attr = self.kwargs[attr].format(*vargs, **kwargs)
                    self.kwargs[attr] = new_attr

        if self.vargs:
            vargs = self.vargs
        if self.kwargs:
            kwargs = self.kwargs
        hist = self.hist_class(*vargs, **kwargs)
        return hist

    def __call__(self, *vargs, **kwargs):
        return self.build(*vargs, **kwargs)
