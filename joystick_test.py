#!/usr/bin/python
import spidev
import os
import time
import math

# 定義通道：此處使用通道 0 為按鈕，1 為操縱桿水平方向，2 為操縱桿垂直方向
swt_channel = 0
vrx_channel = 1
vry_channel = 2

# 讀取間隔時間
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

while True:
    # 讀取操縱桿 X 與 Y 軸的原始數值
    vrx_val = readChannel(vrx_channel)
    vry_val = readChannel(vry_channel)
    # 讀取按鈕（SW）的原始數值
    swt_val = readChannel(swt_channel)
    
    # 根據操縱桿數值計算方向
    direction = get_direction(vrx_val, vry_val, dead_zone)
    
    # 假設按鈕：若數值低於 512 判斷為按下（實際數值依硬體特性調整）
    sw_status = "按下" if swt_val < 512 else "未按下"
    
    print("操縱桿方向: {}  (VRx: {}, Vry: {})  SW: {} ({})".format(direction, vrx_val, vry_val, swt_val, sw_status))
    time.sleep(delay)
