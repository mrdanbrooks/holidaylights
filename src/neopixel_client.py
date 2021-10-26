import board
import neopixel

class NeoPixelClient:
    def __init__(self, num_pixels):
        self.num_pixels = num_pixels
#         self._pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False) # pixel_order = neopixel.GRB
        self._pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False, pixel_order = neopixel.RGB)

    def put_pixels(self, led_values):
            for i in range(self.num_pixels):
                self._pixels[i] = led_values[i]
            self._pixels.show()


