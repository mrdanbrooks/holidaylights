import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame

LED_SIZE = 10  # Diameter of LED
SPACING = 2   # Space between LEDS

COLOR_OFF = (128, 140, 143)

class SimLights(object):
    def __init__(self, num_leds):
        self.num_leds = num_leds

        pygame.init()
#       logo = pygame.image.load("logo32x32.png")
#       pygame.display.set_icon(logo)
        pygame.display.set_caption("Simulated Lights")

        # Set the screen size
        self.screen = pygame.display.set_mode(((LED_SIZE+SPACING)*num_leds + SPACING, LED_SIZE+(SPACING*2)))

        # Initialize LEDS
        self.put_pixels([(0,0,0)]*num_leds)
        
        self.events = list()


    def draw_led(self, led_pos, color):
        """ Draw an individual LED 
        led_pos = integer position from beginning of string 
        color = (r,g,b)
        """
        x_pos = SPACING + (LED_SIZE + SPACING) * led_pos + LED_SIZE/2.0
        y_pos = SPACING + LED_SIZE/2.0
        radius = LED_SIZE / 2.0
        fill = 1 if color == (0, 0, 0) else 0
        color = color if not color == (0, 0, 0) else COLOR_OFF
        pygame.draw.circle(self.screen, color, (x_pos, y_pos), radius, fill)

    def put_pixels(self, led_values):
        # Truncate LED to length we can display
        led_values = led_values[:min(len(led_values), self.num_leds)]
        for i in range(0, len(led_values)):
            self.draw_led(i, led_values[i])
        pygame.display.update()

        # Handle Events
        self.events = pygame.event.get()


    def run_test(self):
        try:
            while True:
                # Put blank pixels
                self.put_pixels([(0,0,0)]*self.num_leds)

                # Read events
                for event in self.events:
                    if event.type == pygame.QUIT:
                        return
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    sim = SimLights(100)
    sim.run_test()

