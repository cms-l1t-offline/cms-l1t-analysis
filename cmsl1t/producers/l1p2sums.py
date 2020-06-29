from __future__ import print_function

from cmsl1t.energySums import EnergySum, Mex, Mey, Met
from .base import BaseProducer


class Producer(BaseProducer):

    def __init__(self, inputs, outputs, **kwargs):
        self._expected_input_order = ['et', 'phi']
        super(Producer, self).__init__(inputs, outputs, **kwargs)

    def produce(self, event):
        setattr(event, self._outputs[0] + '_Met', Met(event['L1PhaseII_puppiMETEt'], event['L1PhaseII_puppiMETPhi']))
        setattr(event, self._outputs[0] + '_MetHF', Met(event['L1PhaseII_puppiMETEt'], event['L1PhaseII_puppiMETPhi']))
        setattr(event, self._outputs[0] + '_Htt', EnergySum(event['L1PhaseII_puppiHT'][0]))

        return True
