from overlay import *
from behaviors import *

def new_years():
    manager = BehaviorManager(50)
    manager.add_behavior_overlay(StaticOn("BLUE"))
    manager.add_behavior_overlay(Sparkle())
#     manager.add_behavior_overlay(MovingPixel())
    manager.start()

def valentines_day():
    import opc
    import time
    import twinkle

    colors = {"OFF": -1.0,
              "WHITE": -1.0,
              "PINK": 110.0,
              "RED": 110.0}


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


if __name__ == "__main__":
    valentines_day()

