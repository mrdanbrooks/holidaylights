from overlay import *
import random
import colorsys
from ledcolor import LEDColor
from collections import deque # For Chasers

class StaticOn(Behavior):
    """ Set all the LEDs to the same color """
    def __init__(self, color):
        print("WARNING: StaticOn is deprecated - use SolidColor instead")
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
        self.red_color = LEDColor("RED")
        self.white_color = LEDColor("WHITE")

    def init(self, leds):
        n = len(leds)
        num_stripes = n // self.stripe_size
        color = "RED"
        for i in range(0, num_stripes):
            # Alternate colors
            color = "WHITE" if color == "RED" else "RED"
            for j in range(0, self.stripe_size):
                leds[i*self.stripe_size + j] = LEDColor(color).get_rgb() 
        # Assign all remaining leds to last color
        for j in range(0, n % self.stripe_size):
            leds[num_stripes*self.stripe_size + j] = LEDColor(color).get_rgb() 

        return leds

    def update(self, leds):
        return leds

    def cancel(self, leds):
        for led in leds:
            update_led_value(led, [0, 0, 0])
        return leds


# SolidColor("OFF")
# AddChasers("RED", 1)
class AddChasers(Behavior):
    """ Spawns color pixels that move in a direction """
    def __init__(self, color, direction, offset=0, spacing=4):
        """
        direction: 1=right, -1=left
        offset: distance from first or last LED to start chasers
        spacing: distance between lit up pixels
        """
        assert(direction in [1, -1])
        self.color = LEDColor(color)
        self.direction = direction
        self.offset = offset
        self.spacing = spacing
        self.led_positions = None # [True, False, False, ...
        

    def init(self, leds):
        self.num_leds = len(leds)
        self.led_positions = deque([False]*self.num_leds)
        # Initialize positions of LEDS
        if self.direction == 1:
            for i in range(0 + self.offset, self.num_leds - 1, self.spacing):
                self.led_positions[i] = True
        else:
            for i in range(self.num_leds - self.offset - 1, 0, -self.spacing):
                self.led_positions[i] = True
        return leds

    def update(self, leds):
        # Rotate led positions 
        self.led_positions.rotate(self.direction)

        for i in range(0, self.num_leds):
            if self.led_positions[i] == True:
                leds[i] = self.color.get_rgb()
        return leds

    def cancel(self, leds):
        for led in leds:
            update_led_value(led, (0, 0, 0))
        return leds
                

# class SeedChasers(Behavior):
#     def __init__(self, color, direction, offset=0, spacing=5):
#         """
#         direction: 1=right, -1=left
#         offset: distance from first or last LED to start chasers
#         spacing: distance between lit up pixels
#         """
#         assert(direction in [1, -1])
#         self.color = LEDColor(color)
#         self.direction = direction
#         self.offset = offset
#         self.spacing = spacing
#         
# 
#     def init(self, leds):
#         self.num_leds = len(leds)
#         # Initialize positions of LEDS
#         if self.direction == 1:
#             for i in range(0 + self.offset, self.num_leds, self.spacing):
#                 leds[i] = self.color.get_rgb()
#         else:
#             for i in range(self.num_leds - self.offset -1, -1, -self.spacing):
#                 leds[i] = self.color.get_rgb()
#         return leds
# 
#     def update(self, leds):
#         """ No-op """
#         return leds
# 
#     def cancel(self, leds):
#         for led in leds:
#             update_led_value(led, [0, 0, 0])
#         return leds
#  
# 
# # Class ColorShifter(color, direction)
# class ColorShifter(Behavior):
#     def __init__(self, color, direction):
#         assert(direction in [1, -1])
#         self.color = LEDColor(color)
#         self.off_color = LEDColor("OFF")
#         self.dir = direction
#         self.num_leds = None
# 
#     def init(self, leds):
#         self.num_leds = len(leds)
#         return leds
# 
# 
#     def update(self, leds):
#         color = self.color.get_rgb()
#         if self.dir == 1:
#             for i in range(0, self.num_leds):
#                 if leds[i][0] == color[0] and leds[i][1] == color[1] and leds[i][2] == color[2]:
#                     leds[(i - 1) % self.num_leds] = [color[0], color[1], color[2]]
#                     print("i=%d  i-1=%d" % (i, ((i - 1) % self.num_leds)))
#                     leds[i] = self.off_color.get_rgb()
#         else:
#             for i in range(self.num_leds - 1, -1, -1):
#                 if leds[i][0] == color[0] and leds[i][1] == color[1] and leds[i][2] == color[2]:
#                     leds[(i + 1) % self.num_leds] = [color[0], color[1], color[2]]
#                     print("i=%d  i+1=%d" % (i, ((i + 1) % self.num_leds)))
#                     leds[i] = self.off_color.get_rgb()
#         print("\n\n")
#         return leds
# 
#     def cancel(self, leds):
#         for led in leds:
#             update_led_value(led, [0, 0, 0])
#         return leds
#  


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
    """
    def __init__(self, color, zone_size=8):
        self.num_leds = None
        self.zone_size = zone_size
        self.zones = list() # [range(0,8), range(8,17), range(17,25), range(25,34), range(34, 42), range(42,50)]
        self.color = LEDColor(color)
        self.current_zone = 1


    def init(self, leds):
        # Number of LEDS in the strand
        self.num_leds = len(leds)
        print("Num Leds = %d" % self.num_leds)
        num_zones = self.num_leds // self.zone_size
        print("Num zones = %d" % num_zones)
        for i in range(0, num_zones):
            self.zones.append(range(i*self.zone_size, i*self.zone_size + self.zone_size))
#         if self.num_leds % self.zone_size > 0:
#             self.zones.append(range(num_zones*self.zone_size, self.num_leds))
        print(self.zones)
        

        return leds

    def update(self, leds):
        target = random.choice(self.zones[self.current_zone])
#         print("zone %d led %d" % (self.current_zone, target))
        update_led_value(leds[target], self.color.get_rgb())
        # select new zone (can't be current zone)
        zones = list(range(0,len(self.zones)))
        zones.pop(zones.index(self.current_zone))
        self.current_zone = random.choice(zones)
        return leds
 
    def cancel(self, leds):
        for led in leds:
            update_led_value(led, (0,0,0))
        return leds



