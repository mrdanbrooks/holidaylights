from overlay import *
from behaviors import *
from led_power_service import LEDPowerClient

CLIENT = "neopixel"



def new_years():
    manager = BehaviorManager(CLIENT, 100)
    manager.add_behavior_overlay(SolidColor("BLUE"))
    manager.add_behavior_overlay(Sparkle("WHITE", zone_size=33))
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
    manager.add_behavior_overlay(SolidColor("GREEN"))
    manager.add_behavior_overlay(Sparkle("YELLOW"))
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


def rainbow():
    manager = BehaviorManager(CLIENT, 100)
    manager.add_behavior_overlay(RainbowColors())
    manager.add_behavior_overlay(Shifter(1))
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
    from deamoneyes import DeamonEyes
    manager = BehaviorManager(CLIENT, 100)
    manager.add_behavior_overlay(Twinkle(colors, 0.01))
    manager.add_behavior_overlay(DeamonEyes(0.01))
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
    christmas_chasers()
#     christmas_multicolor_chasers()
#     christmas_twinkle()
#     christmas_candycane()


def christmas_twinkle():
    colors = ["OFF",
              "RED",
              "GREEN"]
    from twinkle import Twinkle
    manager = BehaviorManager(CLIENT, 100)
    manager.add_behavior_overlay(Twinkle(colors, 0.01))
    manager.loop(0.01)


def christmas_chasers():
    manager = BehaviorManager(CLIENT, 100)
    manager.add_behavior_overlay(SolidColor("OFF"))
    manager.add_behavior_overlay(AddChasers("RED", 1))
    manager.add_behavior_overlay(AddChasers("GREEN", -1))
    manager.loop(0.5)
#     manager.add_behavior_overlay(SeedChasers("RED", 1))
#     manager.add_behavior_overlay(SeedChasers("GREEN", -1, offset=3))
#     manager.add_behavior_overlay(ColorShifter("RED", 1))
#     manager.add_behavior_overlay(ColorShifter("GREEN", -1))


def christmas_multicolor_chasers():
    manager = BehaviorManager(CLIENT, 100)
    manager.add_behavior_overlay(SolidColor("OFF"))
    manager.add_behavior_overlay(AddChasers("RED", 1, spacing=5))
    manager.add_behavior_overlay(AddChasers("GREEN", 1, offset=1, spacing=5))
    manager.add_behavior_overlay(AddChasers("PURPLE", 1, offset=2, spacing=5))
    manager.add_behavior_overlay(AddChasers("BLUE", 1, offset=3, spacing=5))
    manager.add_behavior_overlay(AddChasers("YELLOW", 1, offset=4, spacing=5))
    manager.loop(0.5)

def christmas_candycane():
    manager = BehaviorManager(CLIENT, 100)
    manager.add_behavior_overlay(CandyCaneColors(10))
    manager.add_behavior_overlay(Shifter(1))
    manager.loop(0.08)


def auto_calendar():
    print("Auto Select from Calendar:")
    from datetime import date
    today = date.today()
    year = today.year
    calendar = {(date(year,  1,  1), date(year,  1, 10)): new_years,
                (date(year,  2,  1), date(year,  2, 18)): valentines_day,
                (date(year,  3,  1), date(year,  3, 25)): st_patrick,
                (date(year,  4,  1), date(year,  3, 25)): easter,
                (date(year,  6,  1), date(year,  6, 30)): rainbow,
                (date(year,  7,  1), date(year,  7, 10)): fourthofjuly,
                (date(year, 10,  1), date(year, 11,  3)): halloween,
                (date(year, 11,  4), date(year, 11, 26)): thanksgiving,
                (date(year, 11, 27), date(year, 12, 30)): christmas,
                (date(year, 12, 31), date(year+1, 1, 1)): new_years
                }
    event = None
    for date_range in calendar.keys():
        begin_date, end_date = date_range
        if begin_date <= today <= end_date:
            event = calendar[date_range]
    print(event)
    # Call Event if it exists
    if event:
        event()
                        


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

def main():
#     test_twinkle()
#     test_colors()

    auto_calendar()
#     new_years()
#     valentines_day()
#     st_patrick()
#     easter()
#     rainbow()
#     fourthofjuly()
#     halloween()
#     thanksgiving()
#     candycane()
#     christmas()

if __name__ == "__main__":
    power = LEDPowerClient()
    if power.enable():
        print("LED Power Enabled")
    try:
        main()
    finally:
        if power.disable():
            print("LED Power Disabled")


