# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 14:31:19 2016

@author: gluzhnica
"""
from config import *
from engine import *
from tacton import *

if __name__ == '__main__':
    port = 3  # "COM4"
    baud = 38400
    real_stimulaton = True
    stim_duration = 0.1
    intermediate_duration = 0.05
    intensity = 5
    pulsewidth = 300
    frequency = 99

    if len(sys.argv) > 8:
        baud = int(sys.argv[1])
        port = sys.argv[2]
        stim_duration = float(sys.argv[3])
        intermediate_duration = float(sys.argv[4])
        intensity = int(sys.argv[5])
        pulsewidth = int(sys.argv[6])
        frequency = int(sys.argv[7])
        real_stimulaton = int(sys.argv[8])
    else:
        print ('Usage: ' + sys.argv[0], 'baud port duration bw-duration intensity pulsewidth frequency real_stimulaton')
        sys.exit()

    visuliser = CircularPatternVisualiser()
    visuliser = FilledCircularPatternVisualiser8()

    config = FESStimulationEngineConfig(port, baud)
    engine = FESStimulationEngine(config, real_stimulaton == 0, visuliser)

    sequences = {
        '01_1': [[1]],
        '02_2': [[2]],
        '03_3': [[3]],
        '04_4': [[4]],
        '05_5': [[5]],
        '06_6': [[6]],
        '07_7': [[7]],
        '08_8': [[8]],
        '09_test': [[1], [2]],

        '10_extension': [[5], [8]],
        '11_flexion': [[8], [5]],

        '12_backward': [[6], [7], [2]],
        '13_forward': [[2], [7], [6]],

        '131_down': [[6, 5], [7, 8], [2, 3]],
        '132_up': [[2, 3], [7, 8], [6, 5]],

        '14_suppination': [[6], [1], [2]],
        '15_pronation': [[5], [4], [3]],

        '16_open': [[1], [2, 6], [3, 5]],
        '171_open_key': [[1], [2, 6]],
        '17_open_1': [[7, 8], [1, 4]],

        '18_close': [[3, 5], [2, 6], [1]],
        '18_close_key': [[2, 6], [1]],
        '19_close_1': [[1, 4], [7, 8]],

        '20_left': [[3], [2]],
        '21_left': [[1], [7], [8], [4]],

        '22_right': [[6], [5]],
        '23_right': [[4], [8], [7], [1]],

        '30_progress 1': [[1]],
        '31_progress 2': [[1], [2]],
        '32_progress 3': [[1], [2], [3]],
        '33_progress 4': [[1], [2], [3], [4]],
        '34_progress 5': [[1], [2], [3], [4], [5]],
        '35_progress 6': [[1], [2], [3], [4], [5], [6]],
    }

    shape = SignalShape.TRIANGLE
    shape = SignalShape.SQUARE

    stimtype = StimuliTypes.SPATIO_TEMPORAL_OVERLAPING
    stimtype = StimuliTypes.SPATIO_TEMPORAL

    intensity_min = 3
    patternTactons = []

    for ix in sorted(sequences.keys()):
        sequence = sequences[ix]

        groups = []
        label = ix.split('_')[1]
        for channels in sequence:
            tactons = []
            for channel in channels:
                tacton = SingleTactonFES(stim_duration, frequency, intensity, pulsewidth, channel, intensity_min, shape)
                tactons.append(tacton)

            group = SimultaneousTactonsGroup(stim_duration, tactons, 0.005)
            groups.append(group)

        patternTacton = PatternTacton(intermediate_duration, groups, stimtype, label)
        patternTacton.set_stimulation_type(stimtype)
        patternTactons.append(patternTacton)

    engine.connect()
    engine.set_frequency(frequency)

    def print_help():
        'enter a number between 0 and ', len(sequences) - 1, 'or q to exit'
        for i in range(len(patternTactons)):
            print i, patternTactons[ix].get_label()

    print_help()

    while True:
        line = raw_input()
        if line == "q":
            print('exiting')
            engine.disconnect()
            break

        if line.isdigit():
            ix = int(line)

            if 0 <= ix < len(patternTactons):
                patternTacton = patternTactons[ix]
                engine.stimulate_pattern(patternTacton)
            else:
                print_help()
        else:
            print_help()

        print ''
        print 'eneter a number between 0 and ', len(patternTactons) - 1, 'or q to exit'

    # python stim.py 38400 3 0.2 0.05 4 300 99 1
