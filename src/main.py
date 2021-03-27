from overlay import *
from behaviors import *

def new_years():
    manager = BehaviorManager(50)
    manager.add_behavior_overlay(StaticOn("BLUE"))
    manager.add_behavior_overlay(Sparkle("WHITE"))
#     manager.add_behavior_overlay(MovingPixel())
    manager.start()

def st_patrick():
    manager = BehaviorManager(50)
    manager.add_behavior_overlay(StaticOn("GREEN"))
    manager.add_behavior_overlay(Sparkle("YELLOW"))
#     manager.add_behavior_overlay(MovingPixel())
    manager.start()


def twinkle_wrapper(colors):
    import opc
    import time
    import twinkle

    client = opc.Client('localhost:7890')
    behavior = twinkle.Twinkle(colors)
    try:
        while True:
            leds = behavior.update()
#             print(leds[:5])
            client.put_pixels(leds)
            time.sleep(0.1)
    except KeyboardInterrupt:
        behavior.cancel()


def valentines_day():
    colors = ["OFF",
              "WHITE",
              "PINK",
              "PINK",
              "RED"]
    twinkle_wrapper(colors)

def easter():
    colors = ["OFF",
              "WHITE",
              "PINK",
              "COOLBLUE",
              "TEAL",
              "LIGHTGREEN",
              "GREEN",
              "RED"]
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





if __name__ == "__main__":
#     new_years()
#     valentines_day()
#     st_patrick()
    easter()
#     fourthofjuly()
#     halloween()
#     thanksgiving()
#     christmas()

