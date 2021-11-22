import RPi.GPIO as GPIO
import time

LEDPWR_PIN_OUT = 3   # LED power relay control
LINEPWR_PIN_IN = 4   # LINEPWR (5v wall power) sensing
PWR_EN_PIN_OUT = 14  # PowerBoost Enable

if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
    GPIO.setup(LINEPWR_PIN_IN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(PWR_EN_PIN_OUT, GPIO.OUT)

    print("Setting EN = 1")
    GPIO.output(PWR_EN_PIN_OUT, GPIO.HIGH)
    try:
        while 1:
            if GPIO.input(LINEPWR_PIN_IN):
                print("Power Detected!")
            else:
                print("Power Disconnected!")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Setting EN = 0")
        GPIO.output(PWR_EN_PIN_OUT, GPIO.LOW)
        time.sleep(0.5)
        GPIO.cleanup()
