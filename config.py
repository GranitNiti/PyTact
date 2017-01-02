from abc import ABCMeta

class StimulationEngineConfig:
    __metaclass__ = ABCMeta


class FESStimulationEngineConfig(StimulationEngineConfig):

    def __init__(self, port, baud):
        self.port = port
        self.baud = baud

    def get_port(self):
        return self.port

    def get_baud(self):
        return self.baud

    def set_port(self, port):
        self.port = port

    def set_baud(self, baud):
        self.baud = baud


class VibroStimulationEngineConfig(StimulationEngineConfig):

    def __init__(self, port, baud=115200):
        self.port = port
        self.baud = baud

    def get_port(self):
        return self.port

    def get_baud(self):
        return self.baud

    def set_port(self, port):
        self.port = port

    def set_baud(self, baud):
        self.baud = baud
