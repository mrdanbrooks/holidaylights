from overlay import *
import random
from ledcolor import LEDColor

class EyePixelFader(object):
    def __init__(self, update_rate):
        self._behavior = { "OFF": self._do_off,     # Show background color
                           "DIM": self._do_dim,     # Reduce background color
                           "UP": self._do_up,       # brighten target color
                           "ON": self._do_on,       # hold target color
                           "DOWN": self._do_down,   # reduce target color brightness
                           "LIGHT": self._do_light, # brighten background color
                           "WAIT": self._do_wait    # Show background color, but wait to start new action
                           }
        self._brightness = None
        self._delay_time = None          # Variably determined time to wait
        self._update_rate = update_rate  # program looping rate - used to determine how quickly to decrement delay time
        self._left_eye_background_color = LEDColor("OFF")
        self._right_eye_background_color = LEDColor("OFF")
        self._color = LEDColor("OFF")

        # Constant Parameters
        self._delta = 0.1  # constant brightness step size
        self._static_on_time = 3
        self._static_wait_time = 3

        self._reset()
        
    def _reset(self):
        self._brightness = 0.0
        self._delay_time = 0.0
        self._state = "OFF"

    def _do_off(self):
        """ Show Background color full brightness"""
        self._brightness = 1.0

    def _do_dim(self):
        self._brightness -= self._delta
        if self._brightness < 0.0:
            self._brightness = 0.0
            self._state = "UP"

    def _do_up(self):
        self._brightness += self._delta
        if self._brightness >= 1.0:
            self._brightness = 1.0
            self._state = "ON"
            self._delay_time = self._static_on_time # + random.choice([0.0, 0.1, 0.2, 0.3, 0.4, 0.5])

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
            self._state = "LIGHT"

    def _do_light(self):
        self._brightness += self._delta
        if self._brightness >= 1.0:
            self._brightness = 1.0
            self._state = "WAIT"
            self._delay_time = self._static_wait_time  + random.choice([0.0, 0.1, 0.2, 0.3, 0.4, 0.5])

    def _do_wait(self):
        self._delay_time -= self._update_rate
        if self._delay_time < 0:
            self._delay_time = 0.0
            self._state = "OFF"

    def set_background_colors(self, left_rgb_value, right_rgb_value):
        """ Specify the color the LED should use during OFF, DIM, LIGHT, and WAIT states """
        self._left_eye_background_color.set_color_by_rgb_value(left_rgb_value)
        self._right_eye_background_color.set_color_by_rgb_value(right_rgb_value)

    def start(self, color_name):
        """ Trigger light to begin turning on """
        if not self._state == "OFF":
            raise Exception("Pixel.start() error: Pixel already turned on")
        self._color.set_color(color_name)
        # Change state to DIM
        self._brightness = 1.0
        self._state = "DIM"

    def update(self):
        """ Calculates the new pixel state and brightness settings for this time step
        """
        self._behavior[self._state]()
        self._color.set_brightness(self._brightness)
        self._left_eye_background_color.set_brightness(self._brightness)
        self._right_eye_background_color.set_brightness(self._brightness)

    def cancel(self):
        self._reset()

    def get_state(self):
        """ returns the current state of the pixel (OFF, UP, ON, DOWN, WAIT) """
        return self._state

    def left_eye_rgb_value(self):
        """ returns rgb value
        if Eyes are in UP, ON, or DOWN state, brightness is set against regular color.
        If Eyes are in OFF, DIM, LIGHT, or WAIT states, brightness is set against background color
        """
        return self._color.get_rgb() if self._state in ["UP","ON","DOWN"] else self._left_eye_background_color.get_rgb()

    def right_eye_rgb_value(self):
        """ returns rgb value
        if Eyes are in UP, ON, or DOWN state, brightness is set against regular color.
        If Eyes are in OFF, DIM, LIGHT, or WAIT states, brightness is set against background color
        """
        return self._color.get_rgb() if self._state in ["UP","ON","DOWN"] else self._right_eye_background_color.get_rgb()




class DeamonEyes(Behavior):
    def __init__(self, update_rate, seperation=4):
        self.update_rate = update_rate
        self.num_leds = None
        self.left_eye_location = 90  # Lower value index for eye pair
        self.seperation = seperation # eye pair index offset (gets added to location)

        self.eye_pixel_fader = EyePixelFader(update_rate)

    def init(self, leds):
        self.num_leds = len(leds)
        self.eye_pixel_fader.set_background_colors(leds[self.left_eye_location], leds[self.left_eye_location + self.seperation])
        return leds

    def update(self, leds):
        # Update Eye locations with received background colors
        self.eye_pixel_fader.set_background_colors(leds[self.left_eye_location], leds[self.left_eye_location + self.seperation])

        if self.eye_pixel_fader.get_state() == "OFF":
            #TODO Select new location
            self.eye_pixel_fader.start("RED")

        # Calculate new state and brightness values
        self.eye_pixel_fader.update()

        # Copy values to eye locations
        leds[self.left_eye_location] = self.eye_pixel_fader.left_eye_rgb_value()
        leds[self.left_eye_location + self.seperation] = self.eye_pixel_fader.right_eye_rgb_value()
        return leds


    def cancel(self, leds):
        for led in leds:
            update_led_value(led, (0,0,0))
        return leds



