import RPi.GPIO as GPIO
import threading
from time import sleep

# === LED 控制區 ===
LED_PIN = 16
led_state = False  # 初始狀態為熄滅

def setup_led(gpio):
    GPIO.setup(gpio, GPIO.OUT)
    GPIO.output(gpio, GPIO.LOW)

def control_led(gpio, state):
    global led_state
    if state == 'on':
        GPIO.output(gpio, GPIO.HIGH)
        led_state = True
    elif state == 'off':
        GPIO.output(gpio, GPIO.LOW)
        led_state = False
    else:
        print("無效的狀態，請使用 'on' 或 'off'")

# === 按鈕控制區 ===
BUTTON_PIN = 14  # 根據實際接腳修改

def button_callback(channel):
    global led_state
    print("按鈕被按下")
    if led_state:
        control_led(LED_PIN, 'off')
        print("LED 關閉")
    else:
        control_led(LED_PIN, 'on')
        print("LED 點亮")

def start_button_listener():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    setup_led(LED_PIN)

    GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING,
                          callback=button_callback, bouncetime=300)
    
    def loop():
        while True:
            sleep(1)

    t = threading.Thread(target=loop, daemon=True)
    t.start()

# === 主程式 ===
if __name__ == '__main__':
    try:
        start_button_listener()
        print("按鈕監聽中，按下按鈕以控制 LED...")
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("\n程式結束，清理 GPIO 設定")
    finally:
        GPIO.cleanup()
