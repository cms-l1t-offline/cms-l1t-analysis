from __future__ import print_function

from cmsl1t.energySums import EnergySum, Met
from .base import BaseProducer


class Producer(BaseProducer):

    def __init__(self, inputs, outputs, **kwargs):
        self._expected_input_order = ['phaseIPFJetHt', 'pfMet']
        super(Producer, self).__init__(inputs, outputs, **kwargs)

    def produce(self, event):
        setattr(event, self._outputs[0] + '_Met', Met(event['L1PhaseIPFJet_phaseIPFJetMET'], 0.))
        setattr(event, self._outputs[0] + '_MetHF', Met(event['L1PhaseIPFJet_phaseIPFJetMETHF'], 0.))
        setattr(event, self._outputs[0] + '_Htt', EnergySum(event['L1PhaseIPFJet_phaseIPFJetHt']))

        return True
