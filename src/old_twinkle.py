import opc, time
from ledcolor import LEDColor
import random

import timer

numLEDs = 50 # 512


class BrightnessBehavior(object):
    """ Causes LED brightness to slowly increase, hold on, slowly decrease, then wait before turning on again.
    Pixel Behavior States: OFF > UP > ON > DOWN > WAIT > OFF
    - Calling start() transitions into state "UP"
    - Calling cancel() transitions into state "OFF"

    """
    def __init__(self):
        self.state = "OFF" # OFF, UP, ON, DOWN, WAIT
        self.behavior =  {  "OFF":  self._do_off,
                            "UP":   self._do_up,
                            "ON":   self._do_on,
                            "DOWN": self._do_down,
                            "WAIT": self._do_wait
                            }
        self.brightness = None
        self.delay_time = None

        self.delta = 0.1       # brightness step size
        self.static_on_time = 0.5 #1        # Target Time to spend in ON
        self.random_on_time = 0.5 #1        # Target Time to spend in ON
        self.wait_time = 0.5 #1      # Target Time to spend in WAIT
        #TODO: Must be set to be the same as parent
        self.update_rate = 0.1 # Timer update rate

        self._reset()

    def _reset(self):
        self.brightness = 0.0     # current brightness value
        self.delay_time = 0.0     # Current amount of time spent in ON or WAIT, increments by update_rate
        self.state = "OFF"

    def update(self):
        """ Updates the brightness value based on behavior state. 
        NOTE: This must be called at the same frequency as self.update_rate, or behavior may be incorrect.
        """
        self.behavior[self.state]()


    def start(self):
        if not self.state == "OFF":
            raise Exception("Behavior already started")

        self.state = "UP"

    def cancel(self):
        self._reset()


    def _do_off(self):
        self.brightness = 0.0
        pass

    def _do_up(self):
        self.brightness += self.delta
        if self.brightness >= 1.0:
            self.brightness = 1.0
            self.state = "ON"
            self.random_on_time = random.choice([0.0, 0.1, 0.2, 0.3, 0.4, 0.5])

    def _do_on(self):
        self.delay_time += self.update_rate
        if self.delay_time > self.static_on_time + self.random_on_time:
            self.delay_time = 0.0
            self.state = "DOWN"

    def _do_down(self):
        self.brightness -= self.delta
        if self.brightness < 0.0:
            self.brightness = 0.0
            self.state = "WAIT"

    def _do_wait(self):
        self.delay_time += self.update_rate
        if self.delay_time > self.wait_time:
            self.delay_time = 0.0
            # IMPORTANT: Set state to OFF as the last thing 
            # (this was important for timer, may not still be so imporant)
            self.state = "OFF"

class Pixel(object):
    def __init__(self):
        self.behavior = BrightnessBehavior()
        self.mode = "OFF"
        self.color = LEDColor("OFF")

        if not self.mode == "OFF":
            self.behavior.start()

        self.brightness = 0.0
    
    def get_state(self):
        return self.behavior.state

    def set_color(self, color_name):
        self.color.set_color(color_name)

    def start(self):
        self.behavior.start()

    def update(self):
        self.behavior.update()
        self.color.set_brightness(self.behavior.brightness)
        return self.color.get_rgb()

    def cancel(self):
        self.behavior.cancel()


class Zone(object):
    def __init__(self, zone_num, num_lights, colors):
        self.zone_number = zone_num
        self.num_lights = num_lights
        self.color_names  = colors
        if "OFF" in self.color_names:
            self.color_names.remove("OFF")

        self.pixels = list()
        for i in range(0, self.num_lights):
            self.pixels.append(Pixel())

        self.min_lights = 4
        self.max_lights = 5

        print("Created zone '%d' with %d lights" % (self.zone_number, self.num_lights))

        for n in range(0, self.max_lights):
            self._start_random_pixel_random_color()

    def _start_random_pixel_random_color(self):
        # Select canidate lights that could be turned on, given the following requirements
        # (initially all lights are True, turn some off if they don't meet requirements)
        canidate_lights = [True] * len(self.pixels)
        for i in range(0, len(self.pixels)):
            # Don't choose lights that are already turned on
            if not self.pixels[i].get_state() == "OFF":
                canidate_lights[i] = False
            # Check the light to the left, don't neigboring lights to start at the same time
            if i > 0 and self.pixels[i-1].get_state() == "UP":
                canidate_lights[i] = False
            # Check the light to the right, don't neigboring lights to start at the same time
            if i < (len(self.pixels) - 2) and self.pixels[i+1].get_state() == "UP":
                canidate_lights[i] = False
        # Create array with tuples of (bool,pixel), then select pixels where the bool is true
        off_lights = [pixel for (use_light, pixel) in zip(canidate_lights, self.pixels) if use_light]

        ### NOTE: The above code is a more elaborate version of the single line of code below.
        ### Went with the more complicated version to get slightly better variance in timing.
        # off_lights = [pixel for pixel in self.pixels if pixel.get_state() == "OFF"]

        # If there are any available canidate off lights, turn one on
        if off_lights:
            # Select a light
            pixel = random.choice(off_lights)
            # Select a color
            pixel.set_color(random.choice(self.color_names))
            try:
                pixel.start()
            except:
                print(pixel.get_state())
                exit(0)

    def update(self):
        """ checks pixel states, assigns new behaviors to pixels as needed.
        returns list of updated pixel values for the zone """
        # [db] The code below allow for a random number of lights to be turned off at any given time.
        # This was partly because all the lights had the same timing, and we used the randomness below
        # to prevent all the lights from turning on and off at the same time. 
        # We now vary the length of time a light stays on, so the logic below is no longer needed.
        # Additionally, it looks better when there are more lights turned on at the same time.
        # Therefore, we are skipping this step, and simply calling self._start_random_pixel_random_color()
        # every loop, and allowing it to not do anything if there are no "off lights" to choose from.
#         num_lights = len([x for x in self.pixels if not x.get_state() == "OFF"])
#         # If there are less than N lights on, consider turning a new one on
#         if num_lights < self.min_lights:
#             self._start_random_pixel_random_color()
#         elif num_lights <= self.max_lights:
#             # There is a probability that we don't do it
#             if random.randint(1,100) > 95:
#                 self._start_random_pixel_random_color()
        self._start_random_pixel_random_color()

        return [pixel.update() for pixel in self.pixels]

    def cancel(self):
        for pixel in self.pixels:
            pixel.cancel()

class Twinkle(object):
    def __init__(self, colors):
#         self.zones = [Zone(1, colors), Zone(2, colors), Zone(3, colors), Zone(4, colors), Zone(5, colors), Zone(6, colors), Zone(7, colors), Zone(8, colors), Zone(9, colors), Zone(10, colors)]
#         self.zones = [Zone(1, 5, colors), Zone(2, 5, colors), Zone(3, 5, colors), Zone(4, 5, colors), Zone(5, 5, colors), Zone(6, 5, colors), Zone(7, 5, colors), Zone(8, 5, colors), Zone(9, 5, colors), Zone(10, 5, colors)]
        self.zones = [Zone(1, 16, colors), Zone(2, 17, colors), Zone(3, 17, colors)]

    def update(self):
        # TODO Have each zone set new LEDs

        # Calculate LED values
        led_values = list()
        for zone in self.zones:
            led_values += zone.update()

        return led_values

    def cancel(self):
        for zone in self.zones:
            zone.cancel()

