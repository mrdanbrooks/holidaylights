from overlay import *
import random

class StaticOn(Behavior):
    """ Set all the LEDs to the same color """
    def __init__(self, color):
        self.color = color

    def init(self, leds):
        return self.update(leds)

    def update(self, leds):
        for led in leds:
            update_led_value(led, set_led_color(self.color, 1.0, 1.0))
        return leds

    def cancel(self, leds):
        for led in leds:
            update_led_value(led, set_led_color("OFF", 0.0, 0.0))
        return leds


class MovingPixel(Behavior):
    """ Makes a white pixel move back and forth across the strand """
    def __init__(self):
        self.num_leds = 0

    def init(self, leds):
        self.num_leds = len(leds)
        print("Num Leds = %d" % self.num_leds)
        self.target = 1 # Target LED number to light up
        self.direction = 1  # Direction LED should travel, +1 or -1
        return leds
    
    def update(self, leds):
        update_led_value(leds[self.target], set_led_color("WHITE", 1.0, 1.0))
        if self.direction > 0 and self.target >= self.num_leds -1:
                self.direction = -1
        elif self.direction < 0 and self.target < 1: 
                self.direction = 1 
        self.target += self.direction
        return leds

    def cancel(self, leds):
        for led in leds:
            update_led_value(led, set_led_color("OFF", 0.0, 0.0))
        return leds


class Sparkle(Behavior):
    """ Random LEDs briefly flare and then disappear again
    Assumes 50 lights across 3 windows 
    """
    def __init__(self):
        self.zones = [range(0,8), range(8,17), range(17,25), range(25,34), range(34, 42), range(42,50)]
        self.current_zone = 1


    def init(self, leds):
        # Number of LEDS in the strand
        self.num_leds = len(leds)
        print("Num Leds = %d" % self.num_leds)

        return leds

    def update(self, leds):
        target = random.choice(self.zones[self.current_zone])
#         print("zone %d led %d" % (self.current_zone, target))
        update_led_value(leds[target], set_led_color("WHITE", 1.0, 1.0))
        # select new zone (can't be current zone)
        zones = range(0,len(self.zones))
        zones.pop(zones.index(self.current_zone))
        self.current_zone = random.choice(zones)
        return leds
 
    def cancel(self, leds):
        for led in leds:
            update_led_value(led, set_led_color("OFF", 0.0, 0.0))
        return leds



