import colorsys
# OPC Colors from when RGB channels R and G are switched
# COLORS = {  "OFF":            [0.0,    0.0,  0.0],
# #           Name         HUE     SAT    MAXBRIGHT
#             "WHITE":          [0.0,    0.0,  1.0],
#             "YELLOW":         [60.0,   1.0,  1.0],
#             "ORANGE":         [90.0,   1.0,  1.0],
#             "RED":            [110.0,  1.0,  1.0],
#             "PINK":           [110.0,  0.5,  1.0],
#             "PURPLE":         [180.0,  1.0,  1.0],
#             "LIGHTPURPLE":    [180.0,  0.4,  1.0],
#             "BLUE":           [250.0,  1.0,  1.0],
#             "COOLBLUE":       [300.0,  0.7,  1.0],
#             "TEAL":           [320.0,  1.0,  1.0],
#             "LIGHTGREEN":     [340.0,  0.7,  1.0],
#             "GREEN":          [350.0,  1.0,  1.0],
#             "TEST":           [0, 1.0, 1.0]}

COLORS = {  "OFF":            [0.0,    0.0,  0.0],
#           Name         HUE     SAT    MAXBRIGHT
            "WHITE":          [0.0,    0.0,  1.0],
            "YELLOW":         [60.0,   1.0,  1.0],
            "ORANGE":         [15.0,   1.0,  1.0],
            "RED":            [359.0,  1.0,  1.0],
            "HOTPINK":        [350.0,  1.0,  1.0],
            "PINK":           [0.0,    0.8,  1.0],
            "PURPLE":         [270.0,  1.0,  1.0],
            "LIGHTPURPLE":    [280.0,  0.8,  1.0],
            "BLUE":           [240.0,  1.0,  1.0],
            "COOLBLUE":       [200.0,  0.7,  1.0],
            "TEAL":           [185.0,  1.0,  1.0],
            "LIGHTGREEN":     [100.0,  0.9,  1.0],
            "GREEN":          [110.0,  1.0,  1.0]}



class LEDColor(object):
    """ Define color objects by name """
    def __init__(self, name):
        self._name = name
        self._hue = None
        self._saturation = None
        self._brightness = None
        self._max_brightness = None
        self.set_color(name)

    def set_color(self, name):
        self._hue = COLORS[name][0]
        self._saturation = COLORS[name][1]
        self._brightness = COLORS[name][2]
        self._max_brightness = COLORS[name][2]

    def set_brightness(self, value):
        """ value: 0.0 - 1.0, scales to max brightness"""
        if value > 1.0:
            raise Exception("Value %d greater than 1.0" % value)
        if value < 0.0: 
            raise Exception("Value %d less than 0.0" % value)
        self._brightness = self._max_brightness * value

    def get_color_name(self):
        return self._name

    def get_rgb(self):
        """ returns [r, g, b] scaled 0-255 """
        rgb = colorsys.hsv_to_rgb(self._hue/360.0, self._saturation, self._brightness)
        return [int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)]


