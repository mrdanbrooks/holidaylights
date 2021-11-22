import RPi.GPIO as GPIO
import time

PWR_PIN = 4

if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
    GPIO.setup(PWR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    try:
        while 1:
            if GPIO.input(PWR_PIN):
                print("Power Detected!")
            else:
                print("Power Disconnected!")
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()
