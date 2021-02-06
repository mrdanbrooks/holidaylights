import opc
import time
import colorsys

def set_led_color(color_name, sat, brightness):
    """ Set HSV color to LED RGB value 
    Saturation: 0.0 to 1.0
    Brightness: 0.0 to 1.0
    """
    colors = {"OFF": -1.0,
              "YELLOW": 80.0,
              "ORANGE": 90.0,
              "RED": 110.0,
              "PURPLE": 180.0, 
              "BLUE": 240.0,
              "WHITE": -1.0}
    color = colors[color_name]
    sat = 1.0
    if color_name == "white":
        sat = 0.0
    if color_name == "pink":
        sat = 0.5
#     sat = 1.0 if not color_name == "WHITE" else 0.0
#     print("col=%f"%color)
#     print("Sat=%f"%sat)
#     print("Bri=%f"%brightness)
    rgb = colorsys.hsv_to_rgb(color/360.0, sat, brightness)
#     print(rgb)
    return [int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)]

def update_led_value(led, new):
    """ Update LED triple in place """
    led[0] = new[0]
    led[1] = new[1]
    led[2] = new[2]



class Behavior(object):
    """ A single behavior """
    def __init__(self):
        self.__update_time_step = 0.1

    def init(self, leds):
        """ Initialize the behavior.
        Reads in a list of LEDS.
        Returns a list of LEDS.
        """
        raise NotImplementedError()

    def update(self, leds):
        raise NotImplementedError()

    def cancel(self, leds):
        raise NotImplementedError()

class BehaviorManager(object):
    def __init__(self, num_lights):
        # Behaviors
        self.__overlays = list()

        # Initialize LEDs and their RGB settings
        self.__led_values = list() 
        for i in range(0, num_lights):
            self.__led_values.append(set_led_color("OFF", 0.0, 0.0))

        # Connection to LED controller
        self.__led_client = opc.Client('localhost:7890')

    def add_behavior_overlay(self, behavior):
        assert(isinstance(behavior, Behavior))
        self.__led_values = behavior.init(self.__led_values)
        self.__overlays.append(behavior)

    def start(self):
        try:
            while True:
                for behavior in self.__overlays:
                    self.__leds_values = behavior.update(self.__led_values)
#                 print(len(self.__leds_values))
                self.__led_client.put_pixels(self.__leds_values)
                time.sleep(0.1)
#                 time.sleep(1)
        except KeyboardInterrupt:
             for behavior in self.__overlays:
                self.__leds_values = behavior.cancel(self.__led_values)
             self.__led_client.put_pixels(self.__leds_values)
             time.sleep(0.1)


