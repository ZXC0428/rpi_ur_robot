import RPi.GPIO as GPIO
import threading
import time

# 設定樹梅派的 GPIO 腳位編號 (BOARD 編號)
BUTTON_PIN = 22  # 建議使用穩定且純淨的 Pin 16

def button_action(control_module):
    print("\n" + "="*30)
    print(">>> [硬體訊號] 偵測到按鈕按下！ <<<")
    print("="*30)
    try:
        result = control_module.handle_command("grab")
        print(f"執行狀態: {result}")
    except Exception as e:
        print(f"控制出錯: {e}")

def start_button_listener(control_module):
    """
    使用『輪詢 (Polling)』方式監聽按鈕，避開 Failed to add edge detection 報錯。
    """
    print(f"\n[系統] 啟動按鈕監聽 (方式: 穩定輪詢 / Pin: {BUTTON_PIN})")
    
    GPIO.setwarnings(False)
    try:
        GPIO.setmode(GPIO.BOARD)
    except:
        pass

    # 設定輸入與上拉
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    def polling_loop():
        # 紀錄上一次的狀態，用來偵測「按下」的那一刻（由高變低）
        last_state = GPIO.input(BUTTON_PIN)
        
        while True:
            current_state = GPIO.input(BUTTON_PIN)
            
            # 當狀態從 1 (沒按) 變成 0 (按下) 時
            if last_state == 1 and current_state == 0:
                button_action(control_module)
                # 簡單的防彈跳延遲
                time.sleep(1.0) 
            
            last_state = current_state
            # 每 0.05 秒檢查一次，反應速度足夠快且不佔 CPU
            time.sleep(0.05)

    # 在背景啟動輪詢迴圈
    t = threading.Thread(target=polling_loop, daemon=True)
    t.start()
    print(f"[成功] 按鈕監聽 (Pin {BUTTON_PIN}) 已就緒。")
