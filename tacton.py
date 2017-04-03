from utils import *


class SingleTacton():
    def __init__(self):
        pass


class SingleTactonFES(SingleTacton):
    class_counter = 0

    def __init__(self, duration=0.01, frequency=99, intensity=5, pulsewidth=310, channel=1, minitensity=0,
                 shape=SignalShape.SQUARE):
        self.duration = duration
        self.frequency = frequency
        self.intensity = intensity
        self.pulsewidth = pulsewidth
        self.channel = channel
        self.stype = TactonTypes.FES
        self.shape = shape
        self.minitensity = minitensity
        self.id = SingleTactonFES.class_counter
        SingleTactonFES.class_counter += 1

    def load_from_dict(self, dict_data):
        if 'duration' in dict_data:
            self.set_duration(dict_data['duration'])

        if 'frequency' in dict_data:
            self.set_frequency(dict_data['frequency'])

        if 'intensity' in dict_data:
            self.set_intensity(dict_data['intensity'])

        if 'minitensity' in dict_data:
            self.set_min_intensity(dict_data['minitensity'])

        if 'pulsewidth' in dict_data:
            self.set_pulse_width(dict_data['pulsewidth'])

        if 'channel' in dict_data:
            self.set_channel(dict_data['channel'])

        if 'shape' in dict_data:
            self.set_shape(dict_data['shape'])

    def set_duration(self, duration):
        self.duration = duration

    def set_frequency(self, frequency):
        self.frequency = frequency

    def set_intensity(self, intensity):
        self.intensity = intensity

    def set_min_intensity(self, minitensity):
        self.minitensity = minitensity

    def set_pulse_width(self, pulsewidth):
        self.pulsewidth = pulsewidth

    def set_channel(self, channel):
        self.channel = channel

    def set_shape(self, shape):
        self.shape = shape

    def get_duration(self):
        return self.duration

    def get_frequency(self):
        return self.frequency

    def get_intensity(self):
        return self.intensity

    def get_min_intensity(self):
        return self.minitensity

    def get_pulse_width(self):
        return self.pulsewidth

    def get_channel(self):
        return self.channel

    def get_channels(self):
        return [self.channel]

    def get_shape(self):
        return self.shape

    def is_simple_stimuls(self):
        return self.shape == SignalShape.SQUARE

    def get_id(self):
        return self.id

    def get_size(self):
        return 1


class SingleTactonVibro(SingleTacton):
    class_counter = 0

    def __init__(self, duration=0.01, intensity=255, channel=1, minitensity=0, frequency=100, shape=SignalShape.SQUARE):
        self.duration = duration
        self.intensity = intensity
        self.channel = channel
        self.stype = TactonTypes.VIBRTACTILE
        self.shape = shape
        self.minitensity = minitensity
        self.id = SingleTactonVibro.class_counter
        self.frequency = frequency
        SingleTactonVibro.class_counter += 1

    def load_from_dict(self, dict_data):
        if 'duration' in dict_data:
            self.set_duration(dict_data['duration'])

        if 'intensity' in dict_data:
            self.set_intensity(dict_data['intensity'])

        if 'minitensity' in dict_data:
            self.set_min_intensity(dict_data['minitensity'])

        if 'channel' in dict_data:
            self.set_channel(dict_data['channel'])

        if 'shape' in dict_data:
            self.set_shape(dict_data['shape'])

        if 'frequency' in dict_data:
            self.set_frequency(dict_data['frequency'])

    def set_duration(self, duration):
        self.duration = duration

    def set_intensity(self, intensity):
        self.intensity = intensity

    def set_frequency(self, frequency):
        self.frequency = frequency

    def set_min_intensity(self, minitensity):
        self.minitensity = minitensity

    def set_channel(self, channel):
        self.channel = channel

    def set_shape(self, shape):
        self.shape = shape

    def get_duration(self):
        return self.duration

    def get_intensity(self):
        return self.intensity

    def get_min_intensity(self):
        return self.minitensity

    def get_channel(self):
        return self.channel

    def get_channels(self):
        return [self.channel]

    def get_shape(self):
        return self.shape

    def get_frequency(self):
        return self.frequency

    def is_simple_stimuls(self):
        return self.shape == SignalShape.SQUARE

    def get_id(self):
        return self.id

    def get_size(self):
        return 1


class SimultaneousTactonsGroup:
    class_counter = 0

    def __init__(self, duration=0, tactons=None, delay=0):
        self.delay = delay
        self.tactons = tactons or []
        self.duration = duration
        self.stype = TactonTypes.SIMULTANEUS_GROUP
        self.channels = []
        SingleTactonFES.class_counter += 1
        self.id = SingleTactonFES.class_counter

    def load_from_dict(self, dict_data):
        if 'duration' in dict_data:
            self.set_duration(dict_data['duration'])

        if 'tactons' in dict_data:
            self.tactons = []
            for tacton in dict_data['tactons']:
                if tacton['stype'] == TactonTypes.FES:
                    t = SingleTactonFES()
                    t.load_from_dict(tacton)
                    self.add_tacton(t)
                elif tacton['stype'] == TactonTypes.VIBRTACTILE:  # VibroTactile
                    pass  # handle other type of tactons
                else:
                    pass  # handle more
        self.extract_channels()

    def set_duration(self, duration):
        self.duration = duration

    def set_activation_delay(self, delay):
        self.delay = delay

    def set_tactons(self, tactons):
        self.tactons = tactons

    def get_activation_delay(self):
        return self.delay

    def get_tactons(self):
        return self.tactons

    def get_duration(self):
        return self.duration

    def add_tacton(self, tacton):
        self.tactons.append(tacton)
        self.extract_channels()

    def remove_tacton(self, tacton):
        if tacton in self.tactons:
            self.tactons.remove(tacton)
        self.extract_channels()

    def is_simple_stimuls(self):
        for t in self.tactons:
            if not t.is_simple_stimuls():
                return False
        return True

    def get_channels(self):
        return self.channels

    def extract_channels(self):
        self.channels = []

        for tacton in self.tactons:
            self.channels.append(tacton.get_channel())

        return self.channels

    def get_id(self):
        return self.id

    def get_size(self):
        return len(self.tactons)


class StimulationSlots:
    def __init__(self, tactons=None, intensities=None, gap=0):
        self.gap = gap
        self.tactons = tactons or []
        self.intensities = intensities or []

    def get_gap(self):
        return self.gap

    def get_intensities(self):
        return self.intensities

    def get_tactons(self):
        return self.tactons

    def get_length(self):
        return len(self.tactons)


class PatternTacton:
    def __init__(self, gap=0, tactons=None, stimtype=StimuliTypes.SPATIO_TEMPORAL, label=""):
        self.gap = gap
        self.tactons = tactons or []
        self.stimtype = stimtype
        self.label = label
        # print 'sel.label', label
        self.channels = []
        self.slots = 11
        self.stim_slots = None
        self.context = None
        # print 'stimtype', stimtype

    def load_from_dict(self, dict_data):
        if 'gap' in dict_data:
            self.set_gap(dict_data['gap'])

        if 'stimtype' in dict_data:
            self.set_stimulation_type(dict_data['stimtype'])

        if 'label' in dict_data:
            self.set_label(dict_data['label'])

        if 'tactons' in dict_data:
            self.tactons = []
            for tacton in dict_data['tactons']:
                if tacton['stype'] == TactonTypes.SIMULTANEUS_GROUP:
                    t = SimultaneousTactonsGroup()
                    t.load_from_dict(tacton)
                    self.add_tacton(t)
                elif tacton['stype'] == TactonTypes.FES:
                    t = SingleTactonFES()
                    t.load_from_dict(tacton)
                    self.add_tacton(t)
                elif tacton['stype'] == TactonTypes.VIBRTACTILE:  # VibroTactile
                    pass  # handle other type of tactons
                else:
                    pass  # handle more
            self.extract_channels()

    def set_gap(self, gap):
        self.gap = gap

    def set_label(self, label):
        self.gap = label
        # print 'set_label', label

    def set_tactons(self, tactons):
        self.tactons = tactons

    def set_stimulation_type(self, stimtype):
        self.stimtype = stimtype
        print self.stimtype, stimtype

    def get_gap(self):
        return self.gap

    def get_label(self):
        return self.label

    def get_tactons(self):
        return self.tactons

    def get_stimulation_type(self):
        return self.stimtype

    def add_tacton(self, tacton):
        self.tactons.append(tacton)
        self.extract_channels()

    def remove_tacton(self, tacton):
        if tacton in self.tactons:
            self.tactons.remove(tacton)
        self.extract_channels()

    def is_simple_stimuls(self):
        for t in self.tactons:
            if not t.is_simple_stimuls():
                return False
        return True

    def get_channels(self):
        return self.channels

    def extract_channels(self):
        self.channels = []

        for tacton in self.tactons:
            if isinstance(tacton, SingleTacton):
                self.channels.append(tacton.get_channel())
            elif isinstance(tacton, SimultaneousTactonsGroup):
                self.channels.extend(tacton.get_channels())

        return self.channels

    def get_stimulation_slots(self):
        if self.stim_slots == None:
            self.construct_stimulation_slots()

        return self.stim_slots

    def _get_execution_times(self):
        execution_times = []
        end_time = 0

        for i, tacton in enumerate(self.tactons):
            if i == 0:
                start_time = 0
            else:
                start_time = end_time + self.gap
            end_time = start_time + tacton.get_duration()
            execution_times.append((start_time, end_time))

        return execution_times

    def _get_signal_line(self, slots_nr, shape):
        if shape == SignalShape.TRIANGLE:
            if slots_nr % 2 == 0:
                m = slots_nr / 2
            else:
                m = slots_nr / 2 + 1

            pyramid_scale = [x + 1 if x < m else self.slots - x for x in range(self.slots)]

            return pyramid_scale
        elif shape == SignalShape.LINE_DECRESING:
            return range(slots_nr, 0, -1)
        elif shape == SignalShape.LINE_INCREASING:
            return range(1, slots_nr + 1)
        elif shape == SignalShape.SQUARE:
            return [slots_nr] * slots_nr
        else:
            return [slots_nr] * slots_nr

    def construct_stimulation_slots(self):
        # todo: refactor
        tactons = self.get_tactons()
        tactons_no = len(tactons)
        total_tactons_no = ([t.getSize() for t in tactons])

        if tactons_no == 0:
            return

        gap = self.get_gap()  # gap should be negative for this
        execution_times = self._get_execution_times()

        duration = execution_times[len(execution_times) - 1][1]
        duration / tactons_no

        # print tactons_no, self.slots

        shared_slots = int(
            self.slots * gap * tactons_no / duration)  # if gap is negative they are shared slots, otherwise they are slots in between
        total_slots = tactons_no * self.slots + (tactons_no - 1) * shared_slots
        slot_duration = duration / total_slots

        timeline = 0
        time_slots, start_slots, end_slots = [], {}, {}

        current_slot_id = 0
        to_continue = True
        while timeline <= 2 * duration and to_continue:  # put 2*duration because of float pint errors
            slot_tactons = []

            count_outside = 0

            for i, (start_time, end_time) in enumerate(execution_times):
                tacton = tactons[i]
                # print 'timeline', i, timeline, start_time, end_time , timeline >= start_time, timeline < end_time
                if timeline >= start_time and timeline < end_time:
                    # slot_tactons.append(tacton) # add to execute

                    if isinstance(tacton, SingleTacton):
                        slot_tactons.append(tacton)
                        # print 'single'
                        if tacton.getId() not in start_slots:
                            start_slots[tacton.getId()] = current_slot_id
                    elif isinstance(tacton, SimultaneousTactonsGroup):
                        for chtacton in tacton.get_tactons():
                            slot_tactons.append(chtacton)
                            if chtacton.getId() not in start_slots:
                                start_slots[chtacton.getId()] = current_slot_id

                elif timeline >= end_time:
                    if isinstance(tacton, SingleTacton):
                        if tacton.getId() not in end_slots:
                            end_slots[tacton.get_id()] = current_slot_id
                    elif isinstance(tacton, SimultaneousTactonsGroup):
                        for chtacton in tacton.get_tactons():
                            if chtacton.getId() not in end_slots:
                                end_slots[chtacton.getId()] = current_slot_id

                    count_outside += 1

                    # print 'slot_tactons', slot_tactons
            timeline += slot_duration
            time_slots.append(slot_tactons)
            current_slot_id += 1

            if len(execution_times) == count_outside:
                break

        while len(time_slots[-1]) == 0:
            del time_slots[-1]

        intensities_slot_tacton = {}

        for i, tacton in enumerate(tactons):

            if isinstance(tacton, SingleTacton):
                chtactons = [tacton]
            elif isinstance(tacton, SimultaneousTactonsGroup):
                chtactons = tacton.get_tactons()
            else:
                chtactons = []

            for chtacton in chtactons:
                if chtacton.getId() in intensities_slot_tacton:
                    continue
                slots_nr = end_slots[chtacton.getId()] - start_slots[chtacton.getId()]

                pyramid_scale = self._get_signal_line(slots_nr, chtacton.getShape())
                pyramid_top = max(pyramid_scale)
                intensity = chtacton.getIntensity()
                intensity_min = chtacton.getMinIntensity()
                intensity_range = intensity - intensity_min + 1
                intensities = [intensity_range * x / pyramid_top + intensity_min - 1 for x in pyramid_scale]
                intensities_slot_tacton[chtacton.getId()] = intensities
                # intensities_slot_tacton[tacton.get_id()][chtacton.get_id()] = intensities

        slot_intensities = []

        for s_ix, slot_tactons in enumerate(time_slots):
            slot_intensities.append([])

            # print 's_ix', s_ix, [id(x) for x in slot_tactons]

            for t_ix, tacton in enumerate(slot_tactons):
                # print s_ix, t_ix
                # tacton_intensities = intensities_slot_tacton[tacton.get_id()]
                # print 'tacton_intensities', t_ix, tacton_intensities


                if isinstance(tacton, SingleTacton):
                    chtactons = [tacton]
                elif isinstance(tacton, SimultaneousTactonsGroup):
                    chtactons = tacton.get_tactons()

                # print 'chtactons', len(chtactons)
                # print chtactons#, chtacton_intensities
                for chtacton in chtactons:
                    chtacton_intensities = intensities_slot_tacton[chtacton.getId()]
                    ch_ocurrance = s_ix - start_slots[tacton.get_id()]
                    ch_ocurrance = min((ch_ocurrance, len(chtacton_intensities) - 1))

                    intensity = chtacton_intensities[ch_ocurrance]
                    slot_intensities[s_ix].append(intensity)

        # print len(slot_tactons), slot_tactons, time_slots
        self.stim_slots = StimulationSlots(time_slots, slot_intensities, slot_duration)
