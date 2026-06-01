#!/usr/bin/python
import spidev
import time
import math
import threading
from control.get_position import get_current_tcp_joint_positions
from datetime import datetime

# 定義通道：此處使用通道 0 為按鈕，1 為操縱桿水平方向，2 為操縱桿垂直方向
swt_channel = 0
vrx_channel = 1
vry_channel = 2

# 讀取間隔時間（秒）
delay = 0.5

# 中心點與死區設定（數值範圍 0～1023，中心約為 512）
center = 512
dead_zone = 50  # 在中心 50 的範圍內，視為中立

# 初始化 SPI 介面
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

# 讀取 MCP3008 某個通道的數值（0～1023）
def readChannel(channel):
    val = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((val[1] & 3) << 8) + val[2]
    return data

# 根據操縱桿的 X、Y 軸數值計算出八個方向
def get_direction(vrx, vry, dead_zone):
    dx = vrx - center
    dy = vry - center
    # 如果在死區內，視為中立
    if math.sqrt(dx**2 + dy**2) < dead_zone:
        return "medium"
    # 計算角度（以 X 軸為參考，單位：度）
    theta = (math.degrees(math.atan2(dy, dx)) + 360) % 360

    # 劃分八個方向，每個方向 45 度，中心角分別為：
    # 右：0度；右前：45度；前：90度；左前：135度；
    # 左：180度；左後：225度；後：270度；右後：315度
    if theta < 22.5 or theta >= 337.5:
        return "right"
    elif 22.5 <= theta < 67.5:
        return "right_backward"
    elif 67.5 <= theta < 112.5:
        return "backward"
    elif 112.5 <= theta < 157.5:
        return "left_backward"
    elif 157.5 <= theta < 202.5:
        return "left"
    elif 202.5 <= theta < 247.5:
        return "left_forward"
    elif 247.5 <= theta < 292.5:
        return "forward"
    elif 292.5 <= theta < 337.5:
        return "right_forward"

def joystick_loop(control_module):
    """
    持續讀取操縱桿數值，並根據方向呼叫控制層移動指令。
    當操縱桿處於中立狀態時，發送停止指令。
    為避免重複發送相同指令，僅在方向變化時更新動作。
    """
    prev_direction = "medium"
    while True:
        # 讀取操縱桿 X 與 Y 軸的原始數值
        vrx_val = readChannel(vrx_channel)
        vry_val = readChannel(vry_channel)
        # 讀取按鈕（SW）的原始數值
        swt_val = readChannel(swt_channel)
        
        # 根據操縱桿數值計算方向
        direction = get_direction(vrx_val, vry_val, dead_zone)
        
        # 假設按鈕：若數值低於 512 判斷為按下（依硬體特性調整）
        sw_status = "pressed" if swt_val < 512 else "released"
        
        # print("Joystick direction: {} (VRx: {}, Vry: {})  SW: {} ({})".format(
        #     direction, vrx_val, vry_val, swt_val, sw_status))
        
        # 當方向不為中立且與前次不同時，發送移動指令
        if direction != "medium" and direction != prev_direction:
            result = control_module.handle_move_command(direction)
            # print("Sent move command: {} , result: {}".format(direction, result))
            
            # 取得當前手臂位置
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            tcp_pose, joint_positions = get_current_tcp_joint_positions()
            print(f"Current Time: {current_time}\ntcp_pose={tcp_pose}\noint_positions={joint_positions}\n")

            prev_direction = direction
        # 當方向回到中立時，若前次不為中立，則發送停止指令
        elif direction == "medium" and prev_direction != "medium":
            result = control_module.handle_command("stop")
            # print("Joystick neutral, stop command sent, result: {}".format(result))
            prev_direction = "medium"
        
        time.sleep(delay)

def start_joystick(control_module):
    """
    啟動 joystick 讀取線程，control_module 為已初始化的控制層實例。
    """
    t = threading.Thread(target=joystick_loop, args=(control_module,), daemon=True)
    t.start()
