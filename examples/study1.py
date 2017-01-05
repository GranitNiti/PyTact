from __future__ import division, print_function
import os
import sys
import time
import pandas as pd
import datetime
import pygame
import itertools
import random

sys.path.append("../")
from vis import *
from engine import *
from config import *

__metaclass__ = type


def check_exit(event):
    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
        pygame.quit()
        sys.exit()


def common_pump(event):
    global pause
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            pause = not pause

    check_exit(event)


def check_pause(visualiser):
    global pause

    while pause:
        visualiser.show_text('Paused')
        for event in pygame.event.get():
            common_pump(event)
        pygame.time.wait(50)


def just_wait(duration):
    pygame.time.wait(int(duration))


def show_instruction(visualiser, text):
    visualiser.show_text(text, True)
    visualiser.show_text("Press enter to continue!", False, (0.05 * visualiser.w, 0.9 * visualiser.h))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    visualiser.show_text(text, True)
                    return
            check_exit(event)


def train_tacton(tacton, engine, iterations, logfile, test_instance=False):
    hide = tacton.context
    engine.get_visualiser().set_hide(hide)
    engine.get_visualiser().clear()

    for ix in range(iterations):
        engine.get_visualiser().set_hide(hide)
        engine.get_visualiser().redraw()

        engine.get_visualiser().show_text(tacton.get_label(), False, (0.45 * visualiser.w, 0.1 * visualiser.h), size=6)

        #if not hide:
        just_wait(1000)

        engine.stimulate_pattern(tacton)

        if not test_instance:
            print(datetime.datetime.now(), tacton.get_label(), hide, file=logfile, sep=',')

        engine.get_visualiser().show_text("", True)
        just_wait(1000)
        check_pause(engine.get_visualiser())


def test_tactons(tactons, engine, logfile, round_index, test_instance=True, user=""):
    global pause
    pause = False
    engine.get_visualiser().set_hide(True)
    engine.get_visualiser().clear()

    for tacton in tactons:
        engine.get_visualiser().show_text("Enter Number (press space to repeat):", True)
        just_wait(500)
        start_vibration = datetime.datetime.now()
        engine.stimulate_pattern(tacton)

        answer = None
        counter = 1

        while answer is None:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    #print(pygame.key.name(event.key))

                    if pygame.K_0 <= event.key <= pygame.K_8:
                        answer = pygame.key.name(event.key)

                        if not test_instance:
                            print(user, start_vibration, datetime.datetime.now(), tacton.get_label(), answer, counter,
                                  round_index, tacton.context, file=logfile, sep=',')

                        engine.get_visualiser().show_text(answer, True, size=6)
                        just_wait(1000)

                    elif event.key == pygame.K_SPACE:
                        engine.stimulate_pattern(tacton)

                        if not test_instance:
                            print(user, start_vibration, datetime.datetime.now(), tacton.get_label(), 'REPEAT', counter,
                                  round_index, tacton.context, file=logfile, sep=',')
                        counter = +1

                check_exit(event)
        check_pause(engine.get_visualiser())


if __name__ == "__main__":
    global pause
    start_all = time.time()
    transmit_time = 0.5
    between_time = 0.2
    channels = [1, 2, 3]
    no_choices = 4
    no_rounds = 5
    no_repetitions = 2
    pause = False

    if len(sys.argv) > 4:
        user_code = sys.argv[1]
        out_dir = sys.argv[2]
        transmit_time = float(sys.argv[3])
        between_time = float(sys.argv[4])

    else:
        print('Usage: ' + sys.argv[0],
              ' participant-code output-directory transmit-time between-time')
        sys.exit()

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    ts = datetime.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d_%H_%M_%S')

    test_file_path = os.path.join(out_dir, "test_" + user_code + "_" + ts + '_' + str(transmit_time) + '_' + str(
        between_time) + '.csv')
    train_file_path = os.path.join(out_dir, "train_" + user_code + "_" + ts + '_' + str(transmit_time) + '_' + str(
        between_time) + '.csv')
    tacton_file_path = os.path.join(out_dir, "tacton_" + user_code + "_" + ts + '_' + str(transmit_time) + '_' + str(
        between_time) + '.csv')
    vis_file_path = os.path.join(out_dir, "vis_" + user_code + "_" + ts + '_' + str(transmit_time) + '_' + str(
        between_time) + '.csv')

    print(test_file_path, test_file_path)
    test_file = open(test_file_path, 'w', 0)
    train_file = open(train_file_path, 'w', 0)
    tacton_file = open(tacton_file_path, 'w', 0)
    #vis_file = open(vis_file_path, 'w')

    visualiser = LinePatternVisualiser(no_actuators=3, actuator_radius=50)
    visualiser.set_hide(True)

    #stim_engine = LogStimulationEngine(visualiser=visualiser)
    stim_config = VibroStimulationEngineConfig(port="/dev/cu.usbmodemFD131")
    stim_engine = VibroStimulationEngine(visualiser=visualiser, config=stim_config)

    three_channels = list(itertools.permutations(channels, 3))
    two_channels = list(itertools.permutations(channels, 2))

    random.shuffle(three_channels)
    random.shuffle(two_channels)

    items = two_channels[:no_choices] + three_channels[:no_choices]

    should_vis_two = [True]*int(no_choices/2) + [False]*int(no_choices/2)
    should_vis_three = list(should_vis_two)

    random.shuffle(should_vis_two)
    random.shuffle(should_vis_three)

    should_vis = should_vis_two + should_vis_three

    tactons = []
    demo_tacton_vis, demo_tacton_no_vis = None, None

    for i, item in enumerate(items):
        tacton = PatternTacton(gap=between_time, label=str(i+1))
        tacton.context = should_vis[i]

        for channel in item:
            single_tacton = SingleTactonVibro(duration=transmit_time, intensity=255, channel=channel)
            tacton.add_tacton(single_tacton)

        tactons.append(tacton)

        if tacton.context:
            demo_tacton_no_vis = tacton
        else:
            demo_tacton_vis = tacton

        ch_str = "_".join([str(x) for x in item])
        print(tacton.get_label(), ch_str, tacton.context, file=tacton_file, sep=',')

    tacton_file.close()

    t_tactons = list(tactons)

    show_instruction(stim_engine.get_visualiser(), "Welcome to our study!")
    show_instruction(stim_engine.get_visualiser(), "First you will train!")
    show_instruction(stim_engine.get_visualiser(), "Sometimes you will see a visualisation! e.g:")
    train_tacton(demo_tacton_vis, stim_engine, 2, None, True)
    show_instruction(stim_engine.get_visualiser(), "Sometimes you will not see a visualisation! e.g:")
    train_tacton(demo_tacton_no_vis, stim_engine, 2, None, True)
    show_instruction(stim_engine.get_visualiser(), "Then you will be tested! e.g:")

    test_tactons([t_tactons[0]], stim_engine, None, 0, True, user_code)
    show_instruction(stim_engine.get_visualiser(), "Start when you are ready!")

    print("user", "start", "end", "number", "answer", "couter", "round", "hide", file=test_file, sep=',')

    for r in range(no_rounds):
        for tacton in tactons:
            train_tacton(tacton, stim_engine, no_repetitions, train_file, False)

        for rp in range(no_repetitions):
            random.shuffle(t_tactons)
            test_tactons(t_tactons, stim_engine, test_file, r+1, False, user_code)

    test_file.close()
    train_file.close()

    print('done', start_all, time.time(), time.time() - start_all)

    sys.exit()


