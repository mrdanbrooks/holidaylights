# Author: [db] Dan Brooks
# Based off HTML/JS tutorial by Slawomir Chodnicki, 2019-12-24
# https://towardsdatascience.com/fun-with-html-canvas-lets-make-lava-lamp-plasma-e4b0d89fe778
#
# The effect relies on constructing two height maps (greyscale images), combining subsets from the two
# maps together into constantly changing greyscale gradiants, then colorizing the gradiants. 
#

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame
import numpy as np
import math
import time

def distance(x, y):
    return math.sqrt((x * x) + (y * y))


def height_map_1():
    """
    Produces a centered, circular bull-eye gradiant image
    Returns an image in cv2 format
    """
    width = 1024  # Twice the size of the target image
    height = 1024
    stretch = (3 * math.pi) / (max(width,height) / 2)

    img = np.zeros(shape=(width,height,3), dtype='uint8')
    # U and V are coordinates with origin at upper left
    # CX and CY are coordiantes with origan at center of image
    for u in range(0, img.shape[0]):
        for v in range(0, img.shape[1]):
            cx = u - (width / 2)
            cy = v - (height / 2)
            d = distance(cx, cy)

            ripple = math.sin(d * stretch)
            # normalized 0 to 1
            normalized = (ripple + 1) / 2
            # Normalized 0 to 128
            value = math.floor(normalized * 128)
            # Gray scale value 0-255 (same value on all 3 channels)
            img[u,v,:] = value
    return img


def height_map_2():
    """
    produces an image in cv2 format
    """
    # Height Map 1
    width = 1024  #twice the size of the target image
    height = 1024
    stretch = (3 * math.pi) / (max(width,height) / 2)

    img = np.zeros(shape=(width,height,3), dtype='uint8')
    # U and V are coordinates with origin at upper left
    # CX and CY are coordiantes with origan at center of image
    for u in range(0, img.shape[0]):
        for v in range(0, img.shape[1]):
            cx = u - (width / 2)
            cy = v - (height / 2)
            d1 = distance(0.8 * cx, 1.3 * cy) * 0.022
            d2 = distance(1.35 * cx, 0.45 * cy) * 0.022
            s = math.sin(d1)
            c = math.cos(d2)
            # height value between -2 and +2
            h = s + c
            # heigh value between 0 and 1
            normalized = (h + 2) / 4
            # height value 0 to 127
            value = math.floor(normalized * 127)
            img[u,v,:] = value
    return img


class Plasma(object):
    def __init__(self):
        #TODO: Add width and height inputs for the output image
        # They will be doubled in value to produce the height map dimensions
        print("Initializing now")
        # Compute our two height map gradiants
        self.height_map_1 = height_map_1()
        self.height_map_2 = height_map_2()
        print("done")

    def combined_height_maps(self, dx1=0, dy1=0, dx2=0, dy2=0):
        """
        Returns an np/cv2 image by summing the pixel values of the two heat maps
        """
        # dx1, dy1 and dx2, dy2 -  Offsets for indexing into height_maps
        map_size = 1024
        img_size = 512

        width = img_size
        height = img_size
        h1 = self.height_map_1[dx1:dx1 + width, dy1:dy1 + height]
        h2 = self.height_map_2[dx2:dx2 + width, dy2:dy2 + height]
        return h1 + h2


    def update(self):
        """ Create animation by adding together small windows taken from the two height maps.
        Oscillates the window locations by time.
        Returns a grayscale image
        """

        map_size = 1024
        # Get millisecond since epoch
        t = round(time.time() * 1000)

        # Move height maps
        dx1 = math.floor((((math.cos(t * 0.0002 + 0.4 + math.pi) + 1) / 2)) * (map_size / 2))
        dy1 = math.floor((((math.cos(t * 0.0003 - 0.1) + 1) / 2)) * (map_size / 2))
        dx2 = math.floor((((math.cos(t * -0.0002 + 1.2) + 1) / 2)) * (map_size / 2))
        dy2 = math.floor((((math.cos(t * -0.0003 - 0.8 + math.pi) + 1) / 2)) * (map_size / 2))
        return self.combined_height_maps(dx1=dx1, dy1=dy1, dx2=dx2, dy2=dy2)
        #TODO: Add Color Mapping!
 


class PlasmaSim(object):
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Plasma Sim")
        self.screen = pygame.display.set_mode((512, 512))
        self.plasma = Plasma()

    def run(self):
        try:
            while True:
                img = self.plasma.update()
                surf = pygame.surfarray.make_surface(img)
                self.screen.blit(surf, (0,0))
                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise SystemExit()
        except KeyboardInterrupt:
            pass


def main():
    effect = PlasmaSim()
    effect.run()

if __name__ == "__main__":
    main()
