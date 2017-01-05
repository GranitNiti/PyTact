from vis import *
from tacton import *
from abc import ABCMeta, abstractmethod
from math import *
from utils import *
import serial
from serial import SerialException
import time
import struct
import functools


class StimulationEngine:
    __metaclass__ = ABCMeta

    def __init__(self, config, visualiser=DummyPatternVisualiser(), slots=11):
        self.config = config
        self.connected = False
        self.visualiser = visualiser
        self.slots = slots

    def _init_settings(self):
        m = self.slots / 2 + 1
        self.intensities_pyramid = [x + 1 if x < m else self.slots - x for x in range(self.slots)]
        self.intensities_pyramid_max = max(self.intensities_pyramid)
        self.visualiser.init()

    def connect(self):
        if self.connected:
            return True

        if self._connect():
            self.connected = True
            return True
        else:
            return False

    def disconnect(self):
        if not self.connected:
            return True

        if self._disconnect():
            self.connected = False
            return True
        else:
            return False

    def stimulate_pattern(self, pattern_tacton):
        if pattern_tacton.is_simple_stimuls() and pattern_tacton.get_gap() >= 0:
            for tacton in pattern_tacton.get_tactons():
                self.stimulate_tacton(tacton)

                if pattern_tacton.get_stimulation_type() == StimuliTypes.SPATIO_TEMPORAL:
                    self.stop_stimulation(tacton)

                if pattern_tacton.get_gap() > 0:
                    time.sleep(pattern_tacton.get_gap())

            if pattern_tacton.get_stimulation_type() == StimuliTypes.SPATIO_TEMPORAL_OVERLAPING:
                for tacton in pattern_tacton.get_tactons():
                    self.stop_stimulation(tacton)
        else:
            stimslots = pattern_tacton.get_stimulation_slots()
            self.stimulate_single_tactons_in_slots(stimslots, pattern_tacton.get_tactons())

    def stimulate_single_tactons_in_slots(self, stimslots, all_tactons, stop=True):
        for intensities, tactons in zip(stimslots.get_intensities(), stimslots.get_tactons()):
            self._start_stimulation_tactons(tactons, intensities)
            time.sleep(stimslots.get_gap())

        if stop:
            for tacton in all_tactons:
                self._stop_stimulation(tacton)
                time.sleep(stimslots.get_gap())

    def stimulate_single_tacton_in_slots(self, tacton, stop=True):
        duration = tacton.get_duration()
        intensity = tacton.get_intensity()
        intensity_min = tacton.get_min_intensity()
        intensity_range = intensity - intensity_min + 1

        intensities = [intensity_range * x / self.intensities_pyramid_max + intensity_min - 1 for x in
                       self.intensities_pyramid]

        print 'intensities', self.intensities_pyramid, tacton.get_intensity()

        for i in range(self.slots):
            intensity = intensities[i]
            self._start_stimulation_tacton(tacton, intensity)
            print 'intensity', intensity
            print 'sleep', duration / self.slots
            time.sleep(duration / self.slots)

        if stop:
            self.stop_stimulation(tacton)

    def stimulate_tacton(self, tacton, delay=True):
        if not self.is_connected():
            self.connect()
        self.visualise_stimulation_on(tacton)

        if isinstance(tacton, SingleTacton):
            self._start_stimulation_tacton(tacton)
        elif isinstance(tacton, SimultaneousTactonsGroup):
            for t in tacton.get_tactons():
                self._start_stimulation_tacton(t)

                if tacton.get_activation_delay() > 0:
                    time.sleep(tacton.get_activation_delay())
        if delay:
            time.sleep(tacton.get_duration())

    def stop_stimulation(self, tacton):
        self.visualise_stimulation_off(tacton)
        if isinstance(tacton, SingleTacton):
            self._stop_stimulation(tacton)
        elif isinstance(tacton, SimultaneousTactonsGroup):
            for t in tacton.get_tactons():
                self._stop_stimulation(t)
                if tacton.get_activation_delay() > 0:
                    time.sleep(tacton.get_activation_delay())

    def get_config(self):
        return self.config

    def set_config(self, config):
        self.config = config

    def set_visualiser(self, visualiser):
        self.visualiser = visualiser

    def get_visualiser(self):
        return self.visualiser

    def is_connected(self):
        return self.connected

    def visualise_stimulation_on(self, tacton):
        if isinstance(tacton, SingleTacton):
            self.visualiser.set_actuator_intensity(tacton.get_channel(), tacton.get_intensity())
        elif isinstance(tacton, SimultaneousTactonsGroup):
            channels = [t.get_channel() for t in tacton.get_tactons()]
            intensities = [t.get_intensity() for t in tacton.get_tactons()]
            self.visualiser.set_actuator_intensities(channels, intensities)

    def visualise_stimulation_off(self, tacton):
        if isinstance(tacton, SingleTacton):
            self.visualiser.set_actuator_intensity(tacton.get_channel(), 0)
        elif isinstance(tacton, SimultaneousTactonsGroup):
            channels = [t.get_channel() for t in tacton.get_tactons()]
            intensities = [0] * len(tacton.get_tactons())
            self.visualiser.set_actuator_intensities(channels, intensities)

    @abstractmethod
    def _connect(self):
        print 'not implemented yet - abstract method'

    @abstractmethod
    def _disconnect(self):
        print 'not implemented yet - abstract method'

    @abstractmethod
    def _start_stimulation_tacton(self, tacton, intensitiy):
        print 'not implemented yet - abstract method'

    def _start_stimulation_tactons(self, tactons, intensities):
        for intensity, tacton in zip(intensities, tactons):
            self._start_stimulation_tacton(tacton, intensity)
            time.sleep(0.005)

    @abstractmethod
    def _stop_stimulation(self, tacton):
        print 'not implemented yet - abstract method'


class FESStimulationEngine(StimulationEngine):
    def __init__(self, config, visualiser=DummyPatternVisualiser()):
        self.config = config
        self.connected = False
        self.visualiser = visualiser
        self.fescomm = FESDeviceCommunication()
        self._init_settings()
        # print self.debug

    def set_frequency(self, frequency):
        message = self.fescomm.set_frequency(frequency)
        res = self.ser.write(message)
        return res

    def _connect(self):
        print 'connecting... port:', self.config.get_port(), 'baud', self.config.get_baud()
        try:
            self.ser = serial.Serial(self.config.get_port(), self.config.get_baud())
            print 'open: ', self.ser.isOpen()
            print 'connected'
        except SerialException as err:
            print("OS error: {0}".format(err))
            print("Unexpected error:", sys.exc_info()[0])
            return False

        return True

    def _disconnect(self):
        self.ser.close()
        return True

    def _start_stimulation_tacton(self, tacton, intensity=None):
        i = intensity or tacton.get_intensity()

        message = self.fescomm.encode(tacton.get_channel(), i, tacton.get_pulse_width())
        self.ser.write(message)

    def _stop_stimulation(self, tacton):
        message = self.fescomm.encode(tacton.get_channel(), 0, tacton.get_pulse_width())
        self.ser.write(message)


class FESDeviceCommunication:
    def encode(self, channel, amplitude, pulsewidth):
        sof = [255, 255]
        bytes_no = 4
        command = 1

        if channel < 1 or channel > 8:
            # print 'Error - channel: '+str(channel)+" is not valid it should be between 1-8"
            return None

        if amplitude < -1 or amplitude > 40:
            # print('Error - amplitude: ' + str(amplitude) + ' is not valid it should be between 0 - 20')
            return None

        if pulsewidth < 0 or pulsewidth > 500:
            # print('Error - pulsewidth: ' + str(pulsewidth) + ' is not valid it should be between 0 - 500')
            return None

        pulsewidth1, pulsewidth2 = pulsewidth / 256, pulsewidth % 256
        checksum = sum([bytes_no, command, channel, amplitude, pulsewidth1, pulsewidth2])
        message = [sof[0], sof[1], bytes_no, command, channel, amplitude, pulsewidth1, pulsewidth2, checksum]
        return message

    def set_frequency(self, freq):
        sof = [255, 255]
        bytes_no = 1
        command = 2

        checksum3 = sum([bytes_no, command, freq])
        message = [sof[0], sof[1], bytes_no, command, freq, checksum3]
        return message

    def set_frequency_for_channel(self, freq, ch):
        sof = [255, 255]
        bytes_no = 3
        command = 3

        checksum3 = sum([bytes_no, command, ch, freq])
        message = [sof[0], sof[1], bytes_no, command, ch, freq, checksum3]
        return message


class VibroStimulationEngine(StimulationEngine):
    def __init__(self, config, channels_no=9, visualiser=DummyPatternVisualiser()):
        super(VibroStimulationEngine, self).__init__(config, visualiser)
        #self.config = config
        self.connected = False
        #self.visualiser = visualiser
        self.channelsNo = channels_no
        self._init_settings()
        self.values = [0] * channels_no

    def set_frequency(self, frequency):
        pass

    def _connect(self):
        self.ser = serial.Serial(port=self.config.get_port(), baudrate=self.config.get_baud(), timeout=None,
                                 parity=serial.PARITY_NONE)
        return True

    def _disconnect(self):
        self.ser.close()
        return True

    def _set_vibrators(self, vals):
        magic0 = 0x4B
        magic1 = 0x52
        arr = self._get_rearanged_values(vals)
        checksum = functools.reduce(lambda a, b: a ^ b, arr)
        self.ser.write(struct.pack('B' * (self.channelsNo + 3), magic0, magic1, *(arr + [checksum])))

    def _get_rearanged_values(self, vals):
        nvals = [] + vals
        nvals[2], nvals[6] = nvals[6], nvals[2]
        nvals[0], nvals[8] = nvals[8], nvals[0]
        return nvals

    def _start_stimulation_tacton(self, tacton, intensity=None):
        i = intensity or tacton.get_intensity()
        self.values[tacton.get_channel() - 1] = i
        self._set_vibrators(self.values)

    def _stop_stimulation(self, tacton):
        self.values[tacton.get_channel() - 1] = 0
        self._set_vibrators(self.values)

    def _start_stimulation_tactons(self, tactons, intensities=None):
        if intensities is None:
            for tacton in tactons:
                self.values[tacton.get_channel() - 1] = tacton.get_intensity()
        else:
            for intensity, tacton in zip(intensities, tactons):
                self.values[tacton.get_channel() - 1] = intensity
        self._set_vibrators(self.values)


class LogStimulationEngine(StimulationEngine):
    def __init__(self, visualiser=DummyPatternVisualiser()):
        self.visualiser = visualiser
        self.connected = False
        self.visualiser.init()

    def set_frequency(self, frequency):
        print 'setting frequency to', frequency
        pass

    def _connect(self):
        print 'connecting...'
        self.connected = True
        return True

    def _disconnect(self):
        print 'disconnecting...'
        self.connected = False
        return True

    def _start_stimulation_tacton(self, tacton, intensity=None):
        print 'stimulating single tacton', tacton, intensity
        time.sleep(tacton.get_duration())

    def _stop_stimulation(self, tacton):
        print 'stimulating single tacton', tacton, 0


class TestStimulationEngine(StimulationEngine):
    def __init__(self, visualiser=DummyPatternVisualiser()):
        self.visualiser = visualiser
