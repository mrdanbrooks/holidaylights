import opc, time
import colorsys
import random

import timer

numLEDs = 50 # 512
client = opc.Client('localhost:7890')


class PixelBehavior(object):
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
        self.on_time = 0.5 #1        # Target Time to spend in ON
        self.wait_time = 0.5 #1      # Target Time to spend in WAIT
        self.update_rate = 0.1 # Timer update rate

        self._timer = None
        self._reset()

    def _reset(self):
        self.brightness = 0     # current brightness value
        self.delay_time = 0.0     # Current amount of time spent in ON or WAIT, increments by update_rate

        self._timer = None      # Update Timer object


    def _step(self):
        """ Calls the current behavior """
#         print(self.state, self.brightness)
        self.behavior[self.state]()

    def _do_off(self):
        if self._timer:
            self._timer.cancel()
            time.sleep(0.001)
            self._timer = None

    def _do_up(self):
        self.brightness += self.delta
        if self.brightness >= 1.0:
            self.state = "ON"

    def _do_on(self):
        self.delay_time += self.update_rate
        if self.delay_time > self.on_time:
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
            self._timer.cancel()
            time.sleep(0.001)
            self._timer = None
            # IMPORTANT: Set state to OFF AFTER disabling timer 
            self.state = "OFF"



    def start(self):
        if self._timer:
            raise Exception("Timer already started")

        self.state = "UP"
        self._timer = timer.Timer(self.update_rate, self._step) 
        self._timer.start()

    def cancel(self):
        if self._timer:
            self._timer.cancel()
        time.sleep(0.01)
        self._reset()

class Pixel(object):
    def __init__(self):
        self.behavior = PixelBehavior()
        self.mode = "OFF"
#         self.mode = random.choice(["ORANGE", "PURPLE", "OFF"])
        self.colors = {"OFF": 0.0,
                       "ORANGE": 90.0,
                       "PURPLE": 180.0 }

        self.color = self.colors["ORANGE"]

        if not self.mode == "OFF":
            self.behavior.start()

        self.brightness = 0
    
    def get_state(self):
        return self.behavior.state

    def set_color(self, color):
        self.color = self.colors[color]

    def start(self):
        self.behavior.start()

    def update(self):
        rgb = colorsys.hsv_to_rgb(self.color/360.0, 1.0, self.behavior.brightness)
        return [int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)]

    def cancel(self):
        self.behavior.cancel()


class Zone(object):
    def __init__(self, num):
        self.zone_number = num
        self.pixels = [Pixel(), Pixel(), Pixel(), Pixel(), Pixel()]
        self.min_lights = 2
        self.max_lights = 4

        for n in range(0, self.max_lights):
            self._start_random_pixel_random_color()

    def _start_random_pixel_random_color(self):
        # Select a light
        off_lights = [pixel for pixel in self.pixels if pixel.get_state() == "OFF"]
        pixel = random.choice(off_lights)
        # Select a color
        pixel.set_color(random.choice(["ORANGE", "PURPLE"]))
        try:
            pixel.start()
        except:
            print(pixel.get_state())
            exit(0)

    def update(self):
        """ checks pixel states, assigns new behaviors to pixels as needed.
        returns list of updated pixel values for the zone """
        num_lights = len([x for x in self.pixels if not x.get_state() == "OFF"])
        # If there are less than N lights on, consider turning a new one on
        if num_lights < self.min_lights:
            self._start_random_pixel_random_color()
        elif num_lights < self.max_lights:
            # There is a probability that we don't do it
            if random.randint(1,100) > 95:
                self._start_random_pixel_random_color()

        return [pixel.update() for pixel in self.pixels]

    def cancel(self):
        for pixel in self.pixels:
            pixel.cancel()

class Halloween(object):
    def __init__(self):
        self.zones = [Zone(1), Zone(2), Zone(3), Zone(4), Zone(5), Zone(6), Zone(7), Zone(8), Zone(9), Zone(10)]

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


if __name__ == "__main__":


    client = opc.Client('localhost:7890')
    behavior = Halloween()
    try:
        while True:
            leds = behavior.update()
#             print(leds[:5])
            client.put_pixels(leds)
            time.sleep(0.1)
    except KeyboardInterrupt:
        behavior.cancel()


