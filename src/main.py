from overlay import *
from behaviors import *

CLIENT = "neopixel"

def twinkle_wrapper(colors):
#     import opc
    import neopixel_client
    import time
    import old_twinkle

    client = opc.Client('localhost:7890')
    client = neopixel_client.NeoPixelClient(100)
    behavior = old_twinkle.Twinkle(colors)
    try:
        while True:
            leds = behavior.update()
#             print(leds[:5])
            client.put_pixels(leds)
            time.sleep(0.1)
    except KeyboardInterrupt:
        behavior.cancel()


def new_years():
    manager = BehaviorManager(CLIENT, 100)
    manager.add_behavior_overlay(SolidColor("BLUE"))
    manager.add_behavior_overlay(Sparkle("WHITE"))
#     manager.add_behavior_overlay(MovingPixel())
    manager.loop(0.05)


def valentines_day():
    colors = ["OFF",
              "WHITE",
              "PINK",
              "HOTPINK",
              "RED"]
    from twinkle import Twinkle

    manager = BehaviorManager(CLIENT, 100)
    manager.add_behavior_overlay(Twinkle(colors, 0.01))
    manager.loop(0.01)


def st_patrick():
    manager = BehaviorManager(CLIENT, 100)
#     manager.add_behavior_overlay(StaticOn("GREEN"))
    manager.add_behavior_overlay(SolidColor("GREEN"))
    manager.add_behavior_overlay(Sparkle("YELLOW"))
#     manager.add_behavior_overlay(MovingPixel())
    manager.loop(0.2)


def easter():
    colors = ["YELLOW",
              "PINK",
              "COOLBLUE",
              "LIGHTGREEN",
              "LIGHTPURPLE"]
    from twinkle import Twinkle
    manager = BehaviorManager(CLIENT, 100)
    manager.add_behavior_overlay(Twinkle(colors, 0.01))
    manager.loop(0.01)



def fourthofjuly():
    colors = ["OFF",
              "RED",
              "WHITE",
              "BLUE"]
    from twinkle import Twinkle
    manager = BehaviorManager(CLIENT, 100)
    manager.add_behavior_overlay(Twinkle(colors, 0.01))
    manager.loop(0.01)



def halloween():
    colors = ["OFF",
              "ORANGE",
              "PURPLE"]
    from twinkle import Twinkle
    manager = BehaviorManager(CLIENT, 100)
    manager.add_behavior_overlay(Twinkle(colors, 0.01))
    manager.loop(0.01)



def thanksgiving():
    colors = ["OFF",
              "ORANGE",
              "RED",
              "YELLOW"]
    from twinkle import Twinkle
    manager = BehaviorManager(CLIENT, 100)
    manager.add_behavior_overlay(Twinkle(colors, 0.01))
    manager.loop(0.01)



def christmas():
    colors = ["OFF",
              "RED",
              "GREEN"]
    from twinkle import Twinkle
    manager = BehaviorManager(CLIENT, 100)
    manager.add_behavior_overlay(Twinkle(colors, 0.01))
    manager.loop(0.01)



def rainbow():
    manager = BehaviorManager(CLIENT, 100)
    manager.add_behavior_overlay(RainbowColors())
    manager.add_behavior_overlay(Shifter(1))
    manager.loop(0.01)

def candycane():
    manager = BehaviorManager(CLIENT, 100)
    manager.add_behavior_overlay(CandyCaneColors(10))
    manager.add_behavior_overlay(Shifter(1))
    manager.loop(0.08)

def test_twinkle():
    from twinkle import Twinkle
    colors = ["OFF",
              "WHITE",
              "PINK"]

    manager = BehaviorManager(CLIENT, 1)
    manager.add_behavior_overlay(Twinkle(colors, 0.01))
    manager.loop(0.01)


def test_colors():
#     colors = ["WHITE", "PINK", "RED"]
#     colors = ["GREEN", "YELLOW"]
#     colors = ["YELLOW", "PINK","COOLBLUE","LIGHTGREEN","LIGHTPURPLE"]
#     colors = ["ORANGE","PURPLE","ORANGE","PURPLE"]
    colors = ["ORANGE","PURPLE","ORANGE","PURPLE"]
    manager = BehaviorManager(CLIENT, 100)
    manager.add_behavior_overlay(TestColorPallet(colors))
    manager.loop(0.01)

if __name__ == "__main__":
#     test_twinkle()
#     test_colors()

    new_years()
#     valentines_day()
#     st_patrick()
#     easter()
#     rainbow()
#     fourthofjuly()
#     halloween()
#     thanksgiving()
#     candycane()
#     christmas()

