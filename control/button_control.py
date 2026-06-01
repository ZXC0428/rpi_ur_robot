import RPi.GPIO as GPIO
import threading
from time import sleep
from control.motion_commands import URScriptGenerator
from control.rg_control import RGGrab, Point_triangle, Point0, RGRelease, RGdown

# 設定樹梅派的 GPIO 腳位編號 (BOARD 編號)
BUTTON_PIN = 16  # 實體排針第 16 針

def button_callback(channel, control_module):
    print(f"--- GPIO 偵測到訊號！(Channel: {channel}) ---")
    print("正在執行抓取動作...")
    try:
        result = control_module.handle_command("grab")
        print(f"控制模組回傳結果: {result}")
    except Exception as e:
        print(f"執行指令時發生錯誤: {e}")

def start_button_listener(control_module):
    """
    初始化 GPIO，設定按鈕輸入，並啟動按鈕事件偵測。
    control_module：已初始化的控制層實例，用於執行抓取指令。
    """
    print(f"正在啟動按鈕監聽... (腳位: {BUTTON_PIN}, 模式: BOARD)")
    GPIO.setwarnings(True) # 開啟警告以獲取更多資訊
    try:
        GPIO.setmode(GPIO.BOARD)
    except Exception as e:
        print(f"設定模式時發生提示 (可能已設定): {e}")

    # 設定 BUTTON_PIN 為輸入，並使用上拉電阻
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print(f"腳位 {BUTTON_PIN} 設定完成，當前電位狀態: {GPIO.input(BUTTON_PIN)}")

    # 清理舊的偵測器
    try:
        GPIO.remove_event_detect(BUTTON_PIN)
    except:
        pass

    sleep(0.2)

    # 當檢測到按鈕按下 (FALLING 邊緣) 時呼叫 button_callback
    try:
        GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING,
                              callback=lambda channel: button_callback(channel, control_module),
                              bouncetime=500)
        print("邊緣偵測 (Edge Detection) 已成功掛載。")
    except Exception as e:
        print(f"無法添加邊緣偵測: {e}")

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
