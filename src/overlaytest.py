from overlay import *
from behaviors import *

if __name__ == "__main__":
    manager = BehaviorManager(50)
    manager.add_behavior_overlay(StaticOn("BLUE"))
    manager.add_behavior_overlay(Sparkle())
#     manager.add_behavior_overlay(MovingPixel())
    manager.start()

