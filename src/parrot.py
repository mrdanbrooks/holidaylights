#!/usr/bin/env python3.8
import opc, time
import colorsys

numLEDs = 30 # 512
client = opc.Client('localhost:7890')

def parrot_color(leds):
    """ We receive a series of leds in various colors. Take just the first one
    and make the entire strand that color, in the correct length """
    return [leds[0]] * numLEDs

def duplicate_strands(leds):
    """ Light up two strands with the same set of colors """
    # Fadecandy assumes each strand has 64 LEDs each, and the next strands first pixel address
    # starts where the last strand left off (ie. strand 1 led 1 = address 65)

    # Pad the strand length based on how many actual LEDs we have
    extras = [ (0,0,0)] * (64 - len(leds))
    return leds + extras + leds + extras

class PartyParrotRainbowBehavior():
    """ High level behavior to make the leds rotate in rainbow colorss """
    def __init__(self, size):
        self.leds = [ (0,0,0) ] * size

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
            client.put_pixels(duplicate_strands(parrot_color(self.leds)))
            time.sleep(0.20) 
            self._rotate()

if __name__ == "__main__":
    # Spread colors across 10 slots, but only grab one of them at a time.
    behavior = PartyParrotRainbowBehavior(10)
    behavior.run()
