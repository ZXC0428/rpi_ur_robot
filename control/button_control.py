import RPi.GPIO as GPIO
import threading
from time import sleep
from control.motion_commands import URScriptGenerator
from control.rg_control import RGGrab, Point_triangle, Point0, RGRelease, RGdown

# 設定樹梅派的 GPIO 腳位編號 (BCM 編號)
BUTTON_PIN = 7  # 請依據實際接線修改，例如 GPIO17

def button_callback(channel, control_module):
    print("GPIO 按鈕被按下，執行抓取動作...")
    result = control_module.handle_command("grab")
    print("抓取指令回傳：", result)

def start_button_listener(control_module):
    """
    初始化 GPIO，設定按鈕輸入，並啟動按鈕事件偵測。
    control_module：已初始化的控制層實例，用於執行抓取指令。
    """
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    # 設定 BUTTON_PIN 為輸入，並使用上拉電阻
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    # 當檢測到按鈕按下 (FALLING 邊緣) 時呼叫 button_callback
    GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING,
                          callback=lambda channel: button_callback(channel, control_module),
                          bouncetime=300)
    
    # 為確保程式持續運行，此處啟動一個 daemon 線程作為監聽保持
    def loop():
        while True:
            sleep(1)
    t = threading.Thread(target=loop, daemon=True)
    t.start()
    
    print("GPIO 按鈕監聽已啟動，等待按下觸發抓取指令...")
