from overlay import *
from behaviors import *

CLIENT = "neopixel"

def twinkle_wrapper(colors):
#     import opc
    import neopixel_client
    import time
    import twinkle

    client = opc.Client('localhost:7890')
    client = neopixel_client.NeoPixelClient(100)
    behavior = twinkle.Twinkle(colors)
    try:
        while True:
            leds = behavior.update()
#             print(leds[:5])
            client.put_pixels(leds)
            time.sleep(0.1)
    except KeyboardInterrupt:
        behavior.cancel()


def new_years():
    manager = BehaviorManager(CLIENT, 50)
    manager.add_behavior_overlay(StaticOn("BLUE"))
    manager.add_behavior_overlay(Sparkle("WHITE"))
#     manager.add_behavior_overlay(MovingPixel())
    manager.loop()


def valentines_day():
    colors = ["OFF",
              "WHITE",
              "PINK",
              "PINK",
              "RED"]
    twinkle_wrapper(colors)


def st_patrick():
    manager = BehaviorManager(CLIENT, 100)
    manager.add_behavior_overlay(StaticOn("GREEN"))
    manager.add_behavior_overlay(Sparkle("YELLOW"))
#     manager.add_behavior_overlay(MovingPixel())
    manager.loop()


def easter():
    colors = ["YELLOW",
              "PINK",
              "COOLBLUE",
              "LIGHTGREEN",
              "LIGHTPURPLE"]
    twinkle_wrapper(colors)


def fourthofjuly():
    colors = ["OFF",
              "RED",
              "WHITE",
              "BLUE"]
    twinkle_wrapper(colors)          


def halloween():
    colors = ["OFF",
              "ORANGE",
              "PURPLE"]
    twinkle_wrapper(colors)


def thanksgiving():
    colors = ["OFF",
              "ORANGE",
              "RED",
              "YELLOW"]
    twinkle_wrapper(colors)


def christmas():
    colors = ["OFF",
              "RED",
              "GREEN"]
    twinkle_wrapper(colors)


def rainbow():
    manager = BehaviorManager(CLIENT, 100)
    manager.add_behavior_overlay(RainbowColors())
    manager.add_behavior_overlay(Shifter(1))
    manager.loop(0.01)



if __name__ == "__main__":
    rainbow()
#     new_years()
#     valentines_day()
#     st_patrick()
#     easter()
#     fourthofjuly()
#     halloween()
#     thanksgiving()
#     christmas()

