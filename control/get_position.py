import socket
import struct
from datetime import datetime

# 設定 UR5 機械手臂的 IP
UR5_IP = "192.168.50.155"  # 請根據你的 UR5 設定
PORT = 30003  # 30003 端口可回傳數據
    
def get_current_tcp_joint_positions():
    """ 取得 UR5 當前的關節角度 (qnear) """
    try:
        # 連線到 UR5
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((UR5_IP, PORT))

        # 接收二進制數據
        data = s.recv(1108)
        s.close()

        tcp_pose = struct.unpack('!6d', data[444:492])  # TCP 位姿從第444到492 byte
        joint_positions = struct.unpack('!6d', data[252:300]) # 解析關節角度 (第 252-300 Bytes, 6 個 double)
        tcp_pose = list(tcp_pose)  
        joint_positions = list(joint_positions)

        cmd = f"movej(get_inverse_kin(p{tcp_pose}, qnear={joint_positions}), a=1.3962634015954636, v=1.0471975511965976)" 
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("ur_command.txt", "a") as file:
            file.write(f"{current_time} - {cmd}\n")

        return tcp_pose, joint_positions

    except Exception as e:
        print("錯誤:", e)
        return None