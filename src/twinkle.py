from overlay import *
import random
from ledcolor import LEDColor


class Pixel(object):
    def __init__(self, update_rate):
        self._state = "OFF"   # OFF, UP, ON, DOWN, WAIT
        self._behavior = { "OFF": self._do_off,
                           "UP": self._do_up,
                           "ON": self._do_on,
                           "DOWN": self._do_down,
                           "WAIT": self._do_wait
                           }
        self._brightness = None
        self._delay_time = None          # Variably determined time to wait
        self._update_rate = update_rate  # program looping rate - used to determine how quickly to decrement delay time
        self._color = LEDColor("OFF")

        # Constant Parameters
        self._delta = 0.1  # constant brightness step size
        self._static_wait_time = 0.5

        self._reset()
        
    def _reset(self):
        self._brightness = 0.0
        self._delay_time = 0.0
        self._state = "OFF"

    def _do_off(self):
        self._brightness = 0.0

    def _do_up(self):
        self._brightness += self._delta
        if self._brightness >= 1.0:
            self._brightness = 1.0
            self._state = "ON"
            self._delay_time = self._static_wait_time + random.choice([0.0, 0.1, 0.2, 0.3, 0.4, 0.5])

    def _do_on(self):
        # TODO: Find a more clever way of counting time for each pixel - but not Threaded timers (doesnt work well on pi zero)
        self._delay_time -= self._update_rate
        if self._delay_time < 0:
            self._delay_time = 0.0
            self._state = "DOWN"

    def _do_down(self):
        self._brightness -= self._delta
        if self._brightness < 0.0:
            self._brightness = 0.0
            self._state = "WAIT"
            self._delay_time = self._static_wait_time + random.choice([0.0, 0.1, 0.2, 0.3, 0.4, 0.5])

    def _do_wait(self):
        self._delay_time -= self._update_rate
        if self._delay_time < 0:
            self._delay_time = 0.0
            self._state = "OFF"


    def start(self, color_name):
        """ Trigger light to begin turning on """
        if not self._state == "OFF":
            raise Exception("Pixel.start() error: Pixel already turned on")
        self._color.set_color(color_name)
        self._state = "UP"

    def update(self):
        """ Calculates the new pixel state and brightness settings for this time step
        called by Twinkle.update()
        """
        self._behavior[self._state]()
        self._color.set_brightness(self._brightness)

    def cancel(self):
        self._reset()

    def get_state(self):
        """ returns the current state of the pixel (OFF, UP, ON, DOWN, WAIT) """
        return self._state

    def rgb_value(self):
        """ returns rgb value
        called by Twinkle.update()
        """
        return self._color.get_rgb()


class Twinkle(Behavior):
    def __init__(self, colors_names, update_rate):
        self.update_rate = update_rate  # Track update rate so pixels know how quickly to decrement timers
        self.color_names = colors_names
        self.num_leds = None
        self.pixels = list()

    def init(self, leds):
        """ Initially, all lights are on, turn off lights that don't meet reqiurements later """
        self.num_leds = len(leds)
        self.pixels = list()
        for i in range(0, self.num_leds):
            self.pixels.append(Pixel(self.update_rate))
        return [p.rgb_value() for p in self.pixels]


    def update(self, leds):
        # Select Canidate lights that could be turned on, given the following requirements.
        canidate_lights = [True] * self.num_leds
        for i in range(0, self.num_leds):
            # Dont choose lights that are already on
            if not self.pixels[i].get_state() == "OFF":
                canidate_lights[i] = False
            # Check the light to the left, don't neigboring lights to start at the same time
            if i > 0 and self.pixels[i-1].get_state() == "UP":
                canidate_lights[i] = False
            # Check the light to the right, don't neigboring lights to start at the same time
            if i < (len(self.pixels) - 2) and self.pixels[i+1].get_state() == "UP":
                canidate_lights[i] = False
        # Create array with tuples of (bool,pixel), then select pixels where the bool is true
        canidate_pixels = [pixel for (use_light, pixel) in zip(canidate_lights, self.pixels) if use_light]

        # If there are any available canidate_pixels, Select a single LED to turn on from list of canidates
        if canidate_pixels:
            pixel = random.choice(canidate_pixels)
            try:
                pixel.start(random.choice(self.color_names))
            except:
                print(pixel.get_state())
                exit(0)

        #update each pixel value before reading rgb 
        for pixel in self.pixels:
            pixel.update()

        values =  [p.rgb_value() for p in self.pixels]
        return values

    def cancel(self, leds):
        for pixel in self.pixels:
            pixel.cancel()

        for led in leds:
            update_led_value(led, (0, 0, 0))
        return leds


