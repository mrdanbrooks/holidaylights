import time
from overlay import Behavior
import math

MIN_FIELD_SIZE=40
MAX_FIELD_SIZE=66

class Flag(Behavior):
    def __init__(self, num_leds):
        self.field_flutter = Flutter(MAX_FIELD_SIZE - MIN_FIELD_SIZE) 


    def init(self, leds):
        return leds

    def update(self, leds):

        # Determine stripe size
        stripe_size = (self.num_leds * (2/3)) / 13

        # Determine field size

        return leds

    def cancel(self, leds):
        return [(0,0,0)] * len(leds)

    def get_field_size(self):
        self.field_flutter.update()


class FlutterTest(Behavior):
    def __init__(self, num_leds, velocity=0.01):
        """ 
        num_leds - number of leds to span
        """
        self.flutter = Flutter(num_leds)
        self.num_leds = num_leds

    def init(self, leds):
        return leds

    def update(self, leds):
        pixel_index = self.flutter.update()
        
        # reset leds
        leds = None
        leds = [(0,0,0)] * self.num_leds
        leds[pixel_index] = (255,0,0)
        return leds

    def cancel(self, leds):
        return [(0,0,0)] * len(leds)


class Flutter(object):
    def __init__(self, size, velocity=0.01):
        self.size = size
        self.velocity = velocity

        # Oscillation
        self.theta = 0

    def update(self):
        # move theta around circle from 0 to 2pi
        self.theta = (self.theta + self.velocity) % (2 * math.pi)
        # Oscillate tx between 0 and 1
        tx = (math.cos(self.theta) + 1) / 2.0
        # Scale by size - and round to discrete
        value = round(tx * (self.size - 1))
        return value



def test():
    f = FlutterTest(10)
    try:
        while True:
            f.update(None)
            time.sleep(.2)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    test()
            
