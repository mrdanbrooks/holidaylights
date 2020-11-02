import opc
import time

import twinkle

if __name__ == "__main__":
    colors = {"OFF": -1.0,
              "ORANGE": 90.0,
              "RED": 110.0,
              "YELLOW": 80.0 }


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


