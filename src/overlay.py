# import opc
# import neopixel_client
import time
import colorsys

def old_set_led_color(color_name, sat, brightness):
    """ Set HSV color to LED RGB value 
    Saturation: 0.0 to 1.0
    Brightness: 0.0 to 1.0
    """
    colors = {"OFF": -1.0,
              "YELLOW": 60.0,
              "ORANGE": 90.0,
              "RED": 110.0,
              "PURPLE": 180.0, 
              "BLUE": 240.0,
              "GREEN": 350.0,
              "WHITE": -1.0}
    color = colors[color_name]
    sat = 1.0
    if color_name == "WHITE":
        sat = 0.0
    if color_name == "PINK":
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
    def __init__(self, client, num_lights):
        """
        client = "opc" (for fadecandy) or "neopixel" (for adafruit library)
        """
        # Set size of strand
        self.num_leds = num_lights


        # Behaviors
        self.__overlays = list()

        # Initialize LEDs and their RGB settings
        self.__led_values = list() 
        for i in range(0, num_lights):
            self.__led_values.append([0.0, 0.0, 0.0])

        # Connection to LED controller
        if client == "opc":
            import opc
            class OPCWrapper(opc.Client):
                def put_pixels(self, pixels, channel=0):
                    #TODO: rearrange rgb to grb
                    super().put_pixels(pixels, channel)
#             self.__led_client = opc.Client('localhost:7890')
            self.__led_client = OPCWrapper('localhost:7890')
        elif client == "neopixel":
            import neopixel_client
            self.__led_client = neopixel_client.NeoPixelClient(num_lights)
        elif client == "sim":
            from sim_lights import SimLights
            self.__led_client = SimLights(num_lights)


    def _cancel_behaviors(self):
        """ Call cancel() on all behaviors() """
        for behavior in self.__overlays:
            self.__leds_values = behavior.cancel(self.__led_values)
        self.__led_client.put_pixels(self.__leds_values)
        time.sleep(0.1)


    def add_behavior_overlay(self, behavior):
        assert(isinstance(behavior, Behavior))
        self.__led_values = behavior.init(self.__led_values)
        self.__overlays.append(behavior)


    def loop(self, wait_time=0.01):
        """ Run in a loop """
        while True:
            try:
                self.step()
                time.sleep(wait_time)
            except KeyboardInterrupt:
                self._cancel_behaviors()
                break
    
    def step(self):
        try:
            for behavior in self.__overlays:
                self.__led_values = behavior.update(self.__led_values)
            self.__led_client.put_pixels(self.__led_values)
        except KeyboardInterrupt:
            self._cancel_behaviors()
            raise KeyboardInterrupt

