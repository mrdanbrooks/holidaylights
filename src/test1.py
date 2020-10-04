import opc, time
import colorsys


class Pixel(object):
    def __init__(self):
        """
        off,up,on,down,wait
        """
        self.state = "up"
#         self.color = 90.0 # Orange
        self.color = 180.0 # Purple

        self.rate = 0.01
        self.brightness = 0

    def update(self):
        if self.state == "up":
            if self.brightness >= 1.0:
                self.rate = -self.rate
                self.state = "down"
        elif self.state == "down":
            if self.brightness < 0.0:
                self.rate = -self.rate
                self.state = "up"

        self.brightness += self.rate

        rgb = colorsys.hsv_to_rgb(self.color/360.0, 1.0, self.brightness)
        return [int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)]

class Halloween(object):
    def __init__(self):
        self.leds = list()

if __name__ == "__main__":

    client = opc.Client('localhost:7890')
    pixel = Pixel()
    while True:
        led = pixel.update()
        print(led)
        client.put_pixels([led])
        time.sleep(0.1)


