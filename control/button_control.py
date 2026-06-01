import RPi.GPIO as GPIO
import threading
from time import sleep
from control.motion_commands import URScriptGenerator
from control.rg_control import RGGrab, Point_triangle, Point0, RGRelease, RGdown

# 設定樹梅派的 GPIO 腳位編號 (BOARD 編號)
BUTTON_PIN = 18  # 你目前使用的腳位

def button_callback(channel, control_module):
    print("\n--- [GPIO 訊號觸發] ---")
    try:
        result = control_module.handle_command("grab")
        print(f"執行結果: {result}")
    except Exception as e:
        print(f"執行出錯: {e}")

def start_button_listener(control_module):
    import RPi.GPIO as GPIO
    import time
    
    print(f"\n[系統訊息] 正在啟動實體按鈕監聽器... (Pin {BUTTON_PIN})")
    
    GPIO.setwarnings(False)
    
    # 強制清理該腳位，解決 'Failed to add edge detection' 的關鍵
    try:
        GPIO.setup(BUTTON_PIN, GPIO.IN)
        GPIO.remove_event_detect(BUTTON_PIN)
    except:
        pass

    try:
        GPIO.setmode(GPIO.BOARD)
    except:
        pass

    # 重新設定為輸入 + 上拉電阻
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    # 增加延遲讓系統反應
    time.sleep(0.3)

    try:
        # 將 bouncetime 稍微調高，避免雜訊觸發
        GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING,
                              callback=lambda ch: button_callback(ch, control_module),
                              bouncetime=800)
        print(f"[成功] Pin {BUTTON_PIN} 監聽已掛載。")
    except Exception as e:
        print(f"[嚴重錯誤] 無法監聽 Pin {BUTTON_PIN}: {e}")
        print("請嘗試：1. 換一個腳位 (如 16)  2. 執行 'sudo pkill -f python'")

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
