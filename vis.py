import pygame
from math import cos, sin, pi
import pygame.gfxdraw


class Actuator:
    def __init__(self, _id, x, y, intensity=0):
        self.id = _id
        self.x = x
        self.y = y
        self.intensity = intensity

    def set_id(self, _id):
        self.id = _id

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def set_intensity(self, intensity):
        self.intensity = intensity

    def get_id(self):
        return self.id

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_intensity(self):
        return self.intensity


class PatternVisualiser:
    def __init__(self, actuator_radius=25):
        self.actuator_radius = actuator_radius
        self.actuactors = []

    def init(self):
        self._init()

    def _init(self):
        pygame.init()
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=1)  # setup mixer to avoid sound lag
        pygame.font.init()
        pygame.display.set_caption('Pattern Visualiser')

        info_object = pygame.display.Info()
        self.w, self.h = (info_object.current_w, info_object.current_h)
        self.screen = pygame.display.set_mode((self.w, self.h), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN)
        # w,h = 800,600
        self.w, self.h = int(self.w * 0.5), int(self.h * 0.5)
        self.screen = pygame.display.set_mode((self.w, self.h), pygame.HWSURFACE | pygame.DOUBLEBUF)

        fontpath = pygame.font.match_font('bitstreamverasans')
        self.font = pygame.font.Font(fontpath, int(self.w / 32))

        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.darkBlue = (0, 0, 128)
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.pink = (255, 200, 200)

        self.screen.fill(self.black)
        pygame.display.update()

    def set_actuator_intensity(self, _id, intensity):
        ix = _id - 1
        old_intensity = self.actuactors[ix].get_intensity()
        self.actuactors[ix].set_intensity(intensity)

        if (old_intensity > 0 and intensity == 0) or (old_intensity == 0 and intensity > 0):
            self.draw_stimulation(self.actuactors[ix])

    def set_actuator_intensities(self, ids, intensities):
        for _id, intensity in zip(ids, intensities):
            ix = _id - 1
            self.actuactors[ix].set_intensity(intensity)

        self.draw_current_stimulations()

    def draw_current_stimulations(self):
        self.draw_stimulations(self.actuactors)

    def draw_stimulations(self, actuactors):
        for actuactor in actuactors:
            color = self.green if actuactor.get_intensity() else self.red
            txtcolor = self.blue if actuactor.get_intensity() else self.white
            pygame.gfxdraw.filled_circle(self.screen, actuactor.get_x(), actuactor.get_y(), self.actuator_radius, color)
            font_surface = self.font.render(str(actuactor.get_id()), True, txtcolor)
            sw, sh = font_surface.get_size()
            self.screen.blit(font_surface, (actuactor.get_x() - sw / 2, actuactor.get_y() - sh / 2))

            pygame.display.flip()

    def draw_stimulation(self, actuactor):
        color = self.green if actuactor.get_intensity() else self.red
        txtcolor = self.blue if actuactor.get_intensity() else self.white

        pygame.gfxdraw.filled_circle(self.screen, actuactor.get_x(), actuactor.get_y(), self.actuator_radius, color)

        font_surface = self.font.render(str(actuactor.get_id()), True, txtcolor)
        sw, sh = font_surface.get_size()
        self.screen.blit(font_surface, (actuactor.get_x() - sw / 2, actuactor.get_y() - sh / 2))

        pygame.display.update((actuactor.get_x(), actuactor.get_x(), self.actuator_radius, self.actuator_radius))

    def init_actuators_with_positions(self, positions):
        self.actuactors = []

        for i, (x, y) in enumerate(positions):
            actuactor = Actuator(i + 1, x, y)
            self.actuactors.append(actuactor)

    def quit(self):
        pygame.quit()


class DummyPatternVisualiser(PatternVisualiser):
    def __init__(self, debug=False):
        self.debug = debug
        pass

    def init(self):
        pass

    def set_actuator_intensities(self, ids, intensities):
        if self.debug:
            print 'set_actuator_intensities', ids, intensities

    def set_actuator_intensity(self, _id, intensity):
        if self.debug:
            print 'set_intensity', _id, intensity

    def draw_current_stimulations(self):
        if self.debug:
            print 'draw_current_stimulations'

    def draw_stimulation(self, actuactor):
        if self.debug:
            print 'draw_stimulation', vars(actuactor)

    def init_actuators_with_positions(self, positions):
        if self.debug:
            print 'init_actuators_with_positions', positions

    def quit(self):
        if self.debug:
            print 'quit'


class CircularPatternVisualiser(PatternVisualiser):
    def __init__(self, no_actuators=6, actuator_radius=25):
        self.actuator_radius = actuator_radius
        self.no_actuators = no_actuators

    def init(self):
        self._init()

        half = self.no_actuators / 2
        angels = [pi * x / 3 for x in range(-half, half)]

        center = [self.w / 2, self.h / 2]
        radius = int(0.8 * min(self.w, self.h) / 2)
        positions = [[int(center[0] + (radius * cos(angle))), int(center[1] + (radius * sin(angle)))] for angle in
                     angels]

        for pos in positions:
            pos[0] += int((pos[0] - center[0]) * 0.3)

        if self.no_actuators % 2 > 0:
            positions.append(center)

        self.init_actuators_with_positions(positions)
        self.draw_current_stimulations()


class FilledCircularPatternVisualiser8(PatternVisualiser):
    def __init__(self, actuator_radius=25):
        self.actuator_radius = actuator_radius
        self.no_actuators = 8

    def init(self):
        self._init()

        circle_actuators = 6

        half = circle_actuators / 2
        angels = [pi * x / 3 for x in range(-half, half)]

        center = (self.w / 2, self.h / 2)
        radius = int(0.8 * min(self.w, self.h) / 2)
        positions = [[int(center[0] + (radius * cos(angle))), int(center[1] + (radius * sin(angle)))] for angle in
                     angels]

        for pos in positions:
            pos[0] += int((pos[0] - center[0]) * 0.3)

        positions.append([positions[1][0], self.h / 2])
        positions.append([positions[2][0], self.h / 2])

        self.init_actuators_with_positions(positions)
        self.draw_current_stimulations()


class LinePatternVisualiser(PatternVisualiser):
    def __init__(self, no_actuators=6, actuator_radius=25):
        self.actuator_radius = actuator_radius
        self.no_actuators = no_actuators

    def init(self):
        self._init()

        hstart = self.h / 2
        wstep = (self.w - self.actuator_radius) / (self.no_actuators + 1)
        positions = []

        for i in range(self.no_actuators):
            positions.append([(i + 1) * wstep, hstart])

        self.init_actuators_with_positions(positions)
        self.draw_current_stimulations()


class GridPatternVisualiser(PatternVisualiser):
    def __init__(self, no_rows=2, no_columns=3, actuator_radius=25):
        self.actuator_radius = actuator_radius
        self.no_actuators = no_rows*no_columns
        self.no_rows = no_rows
        self.no_columns = no_columns

    def init(self):
        self._init()

        wstep = (self.w - self.actuator_radius) / (self.no_columns + 1)
        hstep = (self.h - self.actuator_radius) / (self.no_rows + 1)
        positions = []

        for i in range(self.no_rows):
            for j in range(self.no_columns):
                positions.append([(j + 1) * wstep, (i + 1) * hstep])

        self.init_actuators_with_positions(positions)
        self.draw_current_stimulations()


class GenericPatternVisualiser(PatternVisualiser):
    def __init__(self, positions=None, actuator_radius=25):
        self.actuator_radius = actuator_radius
        self.no_actuators = len(acutator_posotions)
        self.positions = positions or []

    def init(self):
        self._init()

        self.init_actuators_with_positions(self.positions)
        self.draw_current_stimulations()


if __name__ == "__main__":
    c = CircularPatternVisualiser()
    c.init()
