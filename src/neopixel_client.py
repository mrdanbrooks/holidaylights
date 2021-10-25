import board
import neopixel

class NeoPixelClient:
    def __init__(self, num_pixels):
        self.num_pixels = num_pixels
#         self.pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False) # pixel_order = neopixel.GRB
        self.pixels = neopixel.NeoPixel(board.D18, num_pixels, auto_write=False, pixel_order = neopixel.GRB)

    def put_pixels(self, led_values):
            print("ledvals = %s" % led_values)
            for i in range(self.num_pixels):
                self.pixels[i] = led_values[i]
            self.pixels.show()
            print("pixels = %s" % self.pixels)


