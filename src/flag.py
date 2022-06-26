import time
from overlay import Behavior
import math
import random

# Field should nominally be around 66
MIN_BODY_SIZE=55
MAX_BODY_SIZE=71

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
################################################################################
################################################################################



class Flag(Behavior):
    def __init__(self, num_leds):
        self.num_leds = num_leds
        num_stripes = 6
        stripes_total_size = int(num_leds * .75)
        stripe_pair_individual_size = int(stripes_total_size / num_stripes)
        self.stripes = list()
        for i in range(0, num_stripes):
            self.stripes.append(StripePair(stripe_pair_individual_size))
        # add last red
        red_size = math.floor(stripe_pair_individual_size/2)
        self.stripes.append(RedResizableRange(math.floor(red_size*0.75), red_size))


    def init(self, leds):
        return leds

    def update(self, leds):
        leds = list()
        for i in range(0, len(self.stripes)):
            leds += self.stripes[i].update()
        # pad with blue
        leds += [(0,0,255)] * (self.num_leds - len(leds))


        return leds

    def cancel(self, leds):
        return [(0,0,0)] * len(leds)

    def get_field_size(self):
        self.field_oscillator.update()

class StripePair(ResizableRange):
    def __init__(self, size):
        super().__init__(math.floor(size*0.75), size)
        self.oscillator.min_velocity = 0.01
        self.oscillator.max_velocity = 0.04
        self.oscillator.velocity = random.choice([0.01, 0.02, 0.03, 0.04])

    def get_pixels(self, size):
        red_size = math.floor(size/2)
        white_size = size - red_size
        reds = [(255,0,0)] * red_size
        whites = [(255, 255, 255)] * white_size
        return reds + whites

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

class RedResizableRange(ResizableRange):
    def __init__(self, min_size, max_size):
        super().__init__(min_size, max_size)

    def get_pixels(self, size):
        return [(255,0,0)] * size


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

class Oscillator(object):
    def __init__(self, size, start_velocity=0.05):
        self._size = size
        self.velocity = start_velocity
        self.min_velocity = 0.03
        self.max_velocity = 0.07
        self.acceleration = 0.01

        # Oscillation
        self.theta = 0

    def size(self):
        return self._size

    def update(self):
        # move theta around circle from 0 to 2pi
        self.theta = (self.theta + self.velocity)
        # Every time we pass 2pi, change velocity
        if self.theta > 2 * math.pi:
            self.theta = self.theta % (2 * math.pi)
            self.velocity += random.choice([-self.acceleration, 0, self.acceleration])
            self.velocity = min(max(self.velocity, self.min_velocity), self.max_velocity)

        # Oscillate tx between 0 and 1
        tx = (math.cos(self.theta) + 1) / 2.0
        # Scale by size - and round to discrete
        value = round(tx * (self._size - 1))
        return value


# class Oscillator(object):
#     def __init__(self, size, velocity=0.01):
#         self._size = size
#         self.velocity = velocity
# 
#         # Oscillation
#         self.theta = 0
# 
#     def size(self):
#         return self._size
# 
#     def update(self):
#         # move theta around circle from 0 to 2pi
#         self.theta = (self.theta + self.velocity) % (2 * math.pi)
#         # Oscillate tx between 0 and 1
#         tx = (math.cos(self.theta) + 1) / 2.0
#         # Scale by size - and round to discrete
#         value = round(tx * (self._size - 1))
#         return value
# 


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
            
