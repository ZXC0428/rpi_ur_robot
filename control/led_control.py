# import time
# import RPi.GPIO as GPIO

# def control_led(gpio, state):
#     """
#     控制 LED 亮滅
    
#     :param gpio: GPIO 引腳號
#     :param state: LED 狀態，'on' 表示點亮，'off' 表示熄滅
#     """
#     # 設定 GPIO 模式及初始化
#     GPIO.cleanup()
#     GPIO.setwarnings(False)
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(gpio, GPIO.OUT)
    
#     try:
#         if state == 'on':
#             GPIO.output(gpio, GPIO.HIGH)  # 點亮 LED
#         elif state == 'off':
#             GPIO.output(gpio, GPIO.LOW)  # 熄滅 LED
#         else:
#             print("無效的狀態，請選擇 'on' 或 'off'")
#     finally:
#         # 清理 GPIO 設定
#         GPIO.cleanup()

import time
import RPi.GPIO as GPIO

_initialized_pins = set()

def init_gpio_once(gpio):
    if gpio not in _initialized_pins:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(gpio, GPIO.OUT)
        _initialized_pins.add(gpio)

def control_led(gpio, state):
    """
    控制 LED 亮滅

    :param gpio: GPIO 引腳號
    :param state: 'on' 或 'off'
    """
    GPIO.setwarnings(False)
    init_gpio_once(gpio)
    
    if state == 'on':
        GPIO.output(gpio, GPIO.HIGH)
    elif state == 'off':
        GPIO.output(gpio, GPIO.LOW)
    else:
        print("無效的狀態，請使用 'on' 或 'off'")

# 清理函數可於程式結束時手動呼叫
def cleanup_led():
    GPIO.cleanup()
