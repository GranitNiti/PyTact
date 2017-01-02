
class StimulationSlot:
    def __init__(self, intensities, duration):
        self.intensities = intensities
        self.duration = duration

    def set_intensities(self, intensities):
        self.intensities = intensities

    def set_duration(self, duration):
        self.duration = duration

    def get_duration(self):
        return self.duration

    def get_intensities(self):
        return self.intensities


class TactonTypes:
    FES = "FES"
    VIBRTACTILE = "VIBRO"
    SIMULTANEUS_GROUP = "SGROUP"


class SignalShape:
    SQUARE = "SQ"
    COS = "COS"
    TRIANGLE = "TR"
    LINE_DECRESING = "LR"
    LINE_INCREASING = "LR"


class StimuliTypes:
    SPATIAL = "S"
    SPATIO_TEMPORAL = "ST"
    SPATIO_TEMPORAL_OVERLAPING = "OST"
    TEMPORAL = "T"
