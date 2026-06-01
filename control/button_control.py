import RPi.GPIO as GPIO
import threading
from time import sleep
from control.motion_commands import URScriptGenerator
from control.rg_control import RGGrab, Point_triangle, Point0, RGRelease, RGdown

# 設定樹梅派的 GPIO 腳位編號 (BOARD 編號)
BUTTON_PIN = 16  # 切換到 Pin 16，避開系統鎖死的 Pin 18

def button_callback(channel, control_module):
    print("\n" + "="*30)
    print(">>> 偵測到實體按鈕按下！ <<<")
    print("="*30)
    try:
        result = control_module.handle_command("grab")
        print(f"執行狀態: {result}")
    except Exception as e:
        print(f"控制出錯: {e}")

def start_button_listener(control_module):
    import RPi.GPIO as GPIO
    import time
    
    print(f"\n[系統] 啟動按鈕監聽 (Pin {BUTTON_PIN} / BOARD)")
    
    GPIO.setwarnings(False)
    
    # 強力清理腳位狀態
    try:
        GPIO.setup(BUTTON_PIN, GPIO.IN)
        GPIO.remove_event_detect(BUTTON_PIN)
    except:
        pass

    try:
        GPIO.setmode(GPIO.BOARD)
    except:
        pass

    # 設定輸入與上拉
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    time.sleep(0.5) # 給系統一點反應時間

    try:
        GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING,
                              callback=lambda ch: button_callback(ch, control_module),
                              bouncetime=1000) # 調高防彈跳時間至 1秒
        print(f"[成功] Pin {BUTTON_PIN} 已就緒。")
    except Exception as e:
        print(f"[失敗] 依然無法掛載 Pin {BUTTON_PIN}: {e}")
        print("提示：請確認沒有其他 Python 程式在背景運行。")

    def loop():
        while True:
            # 每 10 秒印出一次狀態，確認執行緒還活著
            # print(f"監聽執行緒運行中... 腳位 {BUTTON_PIN} 狀態: {GPIO.input(BUTTON_PIN)}")
            sleep(10)
    t = threading.Thread(target=loop, daemon=True)
    t.start()

    print("按鈕監聽啟動程序結束，請嘗試按下按鈕...")
    
    # 為確保程式持續運行，此處啟動一個 daemon 線程作為監聽保持
    def loop():
        while True:
            sleep(1)
    t = threading.Thread(target=loop, daemon=True)
    t.start()
    
    print("GPIO 按鈕監聽已啟動，等待按下觸發抓取指令...")
