from overlay import *
import random
import colorsys
from ledcolor import LEDColor

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
            update_led_value(led, (0, 0, 0))
        return leds

class SolidColor(Behavior):
    """ replacement for StaticOn that doesn't use set_led_color """
    def __init__(self, color):
        self.color = LEDColor(color)

    def init(self, leds):
        return self.update(leds)

    def update(self, leds):
        for led in leds:
            update_led_value(led, self.color.get_rgb())
        return leds

    def cancel(self, leds):
        self.color.set_color("OFF")
        for led in leds:
            update_led_value(led, (0, 0, 0))
        return leds


class TestColorPallet(Behavior):
    """ Test a color pallet by specifying a list of colors
    manager = BehaviorManager(CLIENT, 100)
    manager.add_behavior_overlay(TestColorPallet(["WHITE", "PINK", "RED"]))
    manager.loop(0.01)
    """
    def __init__(self, color_names):
        self.color_pallet = [LEDColor(name) for name in color_names]

    def init(self, leds):
        return self.update(leds)

    def update(self, leds):
        for i in range(0, len(self.color_pallet)):
            leds[i] = self.color_pallet[i].get_rgb()
        return leds

    def cancel(self, leds):
        for color in self.color_pallet:
            color.set_color("OFF")
        for led in leds:
            update_led_value(led, (0, 0, 0))
        return leds



# Class Rainbow - makes a static rainbow
class RainbowColors(Behavior):
    """ Makes a static rainbow across entire LED strip """
    def init(self, leds):
        """ Takes the LED array and assigns each LED a color across a rainbow specrum """
        n = len(leds)
        # Make a rainbow
        for i in range(0, n):
            rgb = colorsys.hsv_to_rgb(float(i) / float(n), 1, 1)
            leds[i] = [int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)]
        return leds

    def update(self, leds):
        return leds

    def cancel(self, leds):
        for led in leds:
            update_led_value(led, (0, 0, 0))
        return leds


class CandyCaneColors(Behavior):
    """ Makes a static candy cane stripping pattern """
    def __init__(self, stripe_size):
        self.stripe_size = stripe_size

    def init(self, leds):
        n = len(leds)
        num_stripes = n // self.stripe_size
        color = "RED"
        for i in range(0, num_stripes):
            # Alternate colors
            color = "WHITE" if color == "RED" else "RED"
            for j in range(0, self.stripe_size):
                leds[i*self.stripe_size + j] = set_led_color(color, 1.0, 1.0)
        # Assign all remaining leds to last color
        for j in range(0, n % self.stripe_size):
            leds[num_stripes*self.stripe_size + j] = set_led_color(color, 1.0, 1.0)

        return leds

    def update(self, leds):
        return leds

    def cancel(self, leds):
        for led in leds:
            update_led_value(led, [0, 0, 0])
        return leds




# Class Shifter(direction, speed)
class Shifter(Behavior):
    """ Shifts all pixels either left or right """
    def __init__(self, direction):
        assert(direction in [1, -1])
        self.dir = direction
        self.num_leds = None

    def init(self, leds):
        self.num_leds = len(leds)
        return leds


    def update(self, leds):
        """ Rotate the LEDS by one position """
        if self.dir == 1:
            buf = leds[0]
            for i in range(0, self.num_leds - 1):
                leds[i] = leds[i + 1]
            leds[self.num_leds - 1] = buf
        else:
            buf = leds[self.num_leds - 1] # Save last LED
            for i in range(self.num_leds - 1, 0, -1):
                leds[i] = leds[i - 1]
            leds[0] = buf
        return leds


    def cancel(self, leds):
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
            update_led_value(led, (0, 0, 0))
        return leds


class Sparkle(Behavior):
    """ Random LEDs briefly flare and then disappear again
    Assumes 50 lights across 3 windows 
    """
    def __init__(self, color):
        self.zones = [range(0,8), range(8,17), range(17,25), range(25,34), range(34, 42), range(42,50)]
        self.color = color
        self.current_zone = 1


    def init(self, leds):
        # Number of LEDS in the strand
        self.num_leds = len(leds)
        print("Num Leds = %d" % self.num_leds)

        return leds

    def update(self, leds):
        target = random.choice(self.zones[self.current_zone])
#         print("zone %d led %d" % (self.current_zone, target))
        update_led_value(leds[target], set_led_color(self.color, 1.0, 1.0))
        # select new zone (can't be current zone)
        zones = list(range(0,len(self.zones)))
        zones.pop(zones.index(self.current_zone))
        self.current_zone = random.choice(zones)
        return leds
 
    def cancel(self, leds):
        for led in leds:
            update_led_value(led, (0,0,0))
        return leds



