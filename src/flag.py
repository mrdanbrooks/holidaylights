import time
from overlay import Behavior
import math

# Field should nominally be around 66
MIN_BODY_SIZE=55
MAX_BODY_SIZE=71

class Flag(Behavior):
    def __init__(self, num_leds):
        self.num_leds = num_leds
        self.field_oscillator = Oscillator(MAX_FIELD_SIZE - MIN_FIELD_SIZE) 


    def init(self, leds):
        return leds

    def update(self, leds):
        # Reset LEDS to blank
        leds = [(0,0,0)] * self.num_leds

        # Determine stripe size
#         stripe_size = (self.num_leds * (2/3)) / 13

        # Determine field size
        oscillator_wave_size = self.field_oscillator.update()
        for i in range(0, MIN_FIELD_SIZE + oscillator_wave_size):
            leds[i] = (0, 0, 255)


        return leds

    def cancel(self, leds):
        return [(0,0,0)] * len(leds)

    def get_field_size(self):
        self.field_oscillator.update()
################################################################################
################################################################################

class TriColorFlag(Behavior):
    def __init__(self, num_leds):
        self.num_leds = num_leds
        self.size = math.floor(num_leds/3)
        self.blue_field = BlueResizableRange(self.size-5, self.size+5)
        self.white_field = WhiteResizableRange(self.size-5, self.size+5)

    def init(self, leds):
        return leds

    def update(self, leds):
        leds = self.blue_field.update() + self.white_field.update()
        # Pad the rest of the field with red
        leds += [(255,0,0)] * (self.num_leds - len(leds))
        return leds

    def cancel(self, leds):
        return [(0,0,0)] * len(leds)


class BlueResizableRange(ResizableRange):
    def __init__(self, min_size, max_size):
        super().__init__(min_size, max_size)

    def get_pixels(self, size):
        return [(0,0,255)] * size


class WhiteResizableRange(ResizableRange):
    def __init__(self, min_size, max_size):
        super().__init__(min_size, max_size)
        self.oscillator.velocity = 0.05

    def get_pixels(self, size):
        return [(255,255,255)] * size

################################################################################
################################################################################

class OscillatorTest(Behavior):
    def __init__(self, num_leds, velocity=0.01):
        """ 
        num_leds - number of leds to span
        """
        self.oscillator = Oscillator(num_leds)
        self.num_leds = num_leds

    def init(self, leds):
        return leds

    def update(self, leds):
        pixel_index = self.oscillator.update()
        
        # reset leds
        leds = None
        leds = [(0,0,0)] * self.num_leds
        leds[pixel_index] = (255,0,0)
        return leds

    def cancel(self, leds):
        return [(0,0,0)] * len(leds)

################################################################################
################################################################################


class ResizableRange(object):
    def __init__(self, min_size, max_size):
        """
        """
        self.min_size = min_size
        self.oscillator = Oscillator(max_size - min_size)

    def get_pixels(self, num_pixels):
        """ return list of pixels [(r,g,b), ...]
        must be the length of num_pixels
        This should be overwritten by inheriting classes
        """
        return [(0,0,0)]*num_pixels

    def update(self):
        """ return just the pixels for this range """
        # Calculate the length of pixels to return
        dynamic_size = self.oscillator.update()
        size = self.min_size + dynamic_size
        return self.get_pixels(size)


class Oscillator(object):
    def __init__(self, size, velocity=0.01):
        self._size = size
        self.velocity = velocity

        # Oscillation
        self.theta = 0

    def size(self):
        return self._size

    def update(self):
        # move theta around circle from 0 to 2pi
        self.theta = (self.theta + self.velocity) % (2 * math.pi)
        # Oscillate tx between 0 and 1
        tx = (math.cos(self.theta) + 1) / 2.0
        # Scale by size - and round to discrete
        value = round(tx * (self._size - 1))
        return value



def test():
    f = OscillatorTest(10)
    try:
        while True:
            f.update(None)
            time.sleep(.2)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    test()
            
