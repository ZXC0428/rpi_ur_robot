#!/usr/bin/python
import spidev
import time
import math
import socket

# -------------------------
# 設定 MCP3008 的通道
# -------------------------
swt_channel = 0    # 按鈕通道（此處未用於速度控制，可依需求擴充）
vrx_channel = 1    # 搖桿水平方向
vry_channel = 2    # 搖桿垂直方向

# -------------------------
# 參數設定
# -------------------------
update_interval = 0.1   # 每 0.1 秒更新一次
center = 512            # 中心值（0～1023）
dead_zone = 50          # 死區範圍（中心附近視為中立）
max_deflection = (512 - dead_zone)  # 最大有效偏移（大約 462）
max_speed = 0.2         # 最大速度（m/s，可依實際需求調整）
decel_factor = 0.8      # 平滑減速比例
min_speed_threshold = 0.01  # 當速度低於此值時視為停止

# -------------------------
# 初始化 SPI 介面
# -------------------------
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

def readChannel(channel):
    """讀取 MCP3008 指定通道的數值 (0~1023)"""
    val = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((val[1] & 3) << 8) + val[2]
    return data

# -------------------------
# 利用 socket 發送速度指令給 UR5
# -------------------------
def send_robot_velocity_command(vx, vy, sock):
    """
    使用 URScript 的 speedl 指令設定機械手臂在笛卡爾空間的速度。
    指令格式：speedl([vx, vy, vz, rx, ry, rz], acceleration, time_horizon)
    此處假設 vz=0、rx=ry=rz=0，acceleration 固定為 1.2，time_horizon 取 update_interval。
    """
    a = 1.2
    t_val = update_interval
    # 組合指令
    # 注意：末尾必須有換行符號，確保指令完整送出
    command = f"speedl([{vx:.3f}, {vy:.3f}, 0, 0, 0, 0], {a}, {t_val})\n"
    try:
        sock.sendall(command.encode('utf-8'))
        print("【發送指令】", command.strip())
    except Exception as e:
        print("Socket 發送錯誤:", e)

# -------------------------
# 建立與 UR5 的 Socket 連線
# -------------------------
UR5_IP = "192.168.50.155"  # 根據實際情況修改
UR5_PORT = 30002         # UR5 控制埠通常為 30002
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect((UR5_IP, UR5_PORT))
    print("成功連線至 UR5")
except Exception as e:
    print("無法連線至 UR5:", e)
    exit(1)

# -------------------------
# 主迴圈：讀取搖桿、計算速度、發送指令
# -------------------------
current_vx = 0.0
current_vy = 0.0

while True:
    # 讀取操縱桿原始數值
    vrx_val = readChannel(vrx_channel)
    vry_val = readChannel(vry_channel)
    # 按鈕數值讀取（此範例未使用，可擴充）
    swt_val = readChannel(swt_channel)
    
    # 計算搖桿在 X、Y 軸的偏移量
    dx = vrx_val - center
    dy = vry_val - center
    magnitude = math.sqrt(dx**2 + dy**2)
    
    if magnitude >= dead_zone:
        # 有效偏移（扣除死區）
        effective_magnitude = magnitude - dead_zone
        if effective_magnitude > max_deflection:
            effective_magnitude = max_deflection
        # 以線性映射計算速度
        speed = (effective_magnitude / max_deflection) * max_speed
        theta = math.atan2(dy, dx)
        desired_vx = speed * math.cos(theta)
        desired_vy = speed * math.sin(theta)
        current_vx = desired_vx
        current_vy = desired_vy
    else:
        # 若在死區內，進行平滑減速
        current_vx *= decel_factor
        current_vy *= decel_factor
        if math.sqrt(current_vx**2 + current_vy**2) < min_speed_threshold:
            current_vx = 0.0
            current_vy = 0.0
    
    print("VRx: {}, Vry: {}  =>  vx = {:.3f} m/s, vy = {:.3f} m/s".format(
          vrx_val, vry_val, current_vx, current_vy))
    
    # 使用 socket 發送速度指令
    send_robot_velocity_command(current_vx, current_vy, sock)
    
    time.sleep(update_interval)
