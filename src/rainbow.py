#!/usr/bin/env python
import opc, time
import colorsys

numLEDs = 48 # 512
client = opc.Client('localhost:7890')


class RainbowBehavior():
    """ High level behavior to make the leds rotate in rainbow colorss """
    def __init__(self):
        self.leds = [ (0,0,0) ] * numLEDs

    def _rainbow(self):
        """ Takes the LED array and assigns each LED a color across a rainbow specrum """
        n = len(self.leds)
        # Make a rainbow
        for i in range(0, n):
            rgb = colorsys.hsv_to_rgb(float(i) / float(n), 1, 1)
            self.leds[i] = [int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)]

    def _rotate(self):
        """ Rotate the LEDs by one position """
        # Rotate the LED positions
        buf = self.leds[0]
        for i in range(0, len(self.leds) - 1):
            self.leds[i] = self.leds[i + 1]
        self.leds[len(self.leds) - 1] = buf

    def run(self):
        """ Main loop that runs the rainbow behavior """
        self._rainbow()
        while True:
            client.put_pixels(self.leds)
            time.sleep(0.09) # 0.03
            self._rotate()

if __name__ == "__main__":
    behavior = RainbowBehavior()
    behavior.run()
