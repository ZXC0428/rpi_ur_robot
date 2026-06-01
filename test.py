# import RPi.GPIO as GPIO
# from time import sleep

# btn_pin = 8
# GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(btn_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# while True:
#   if GPIO.input(btn_pin) == GPIO.HIGH:
#     print("按下按鈕")
#   elif GPIO.input(btn_pin) == GPIO.LOW:
#     print("未按下按鈕")
#   sleep(0.2)

import time
import RPi.GPIO as GPIO

def control_led(gpio, state):
    """
    控制 LED 亮滅
    
    :param gpio: GPIO 引腳號
    :param state: LED 狀態，'on' 表示點亮，'off' 表示熄滅
    """
    # 設定 GPIO 模式及初始化
    GPIO.cleanup()
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpio, GPIO.OUT)
    
    try:
        if state == 'on':
            GPIO.output(gpio, GPIO.HIGH)  # 點亮 LED
        elif state == 'off':
            GPIO.output(gpio, GPIO.LOW)  # 熄滅 LED
        else:
            print("無效的狀態，請選擇 'on' 或 'off'")
    finally:
        # 清理 GPIO 設定
        GPIO.cleanup()

control_led(20, "off")