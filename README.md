# PyTacton
#Code sample for creating an stimulation engine, creating a complex pattern and stimulating it

#step 1 - creating a visualiser
vis = LinePatternVisualiser(no_actuators=3)

#step 2 - creating a stimulation engine - hardware device
cfg = VibroStimulationEngineConfig(port="/dev/cu.usbFA1")
eng = VibroStimulationEngine(visualiser=vis, config=cfg)

#step 3 - creating a pattern composed of three motors:
t1 = SingleTactonVibro(duration=0.5, channel=1)
t2 = SingleTactonVibro(duration=0.5, channel=2)
t3 = SingleTactonVibro(duration=0.5, channel=3)
tacton = PatternTacton(gap=0.2, tactons=[t1, t3, t2])

#step 4 - stimulating the tacton
eng.stimulate_pattern(tacton)