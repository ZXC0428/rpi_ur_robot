import logging
from time import sleep
from comm.socket_client import SocketClient
from control.motion_commands import URScriptGenerator
from utils.boundary_checker import is_within_boundaries
from control.rg_control import RGGrab, Point_triangle, Point0, RGRelease

# 請根據您的 UR5 控制器設定 IP 與 Port
UR5_IP = "192.168.50.155"
UR5_PORT = 30002

class ControlModule:
    def __init__(self):
        self.state = "idle"
        self.logger = logging.getLogger("ControlModule")
        self.socket_client = SocketClient(UR5_IP, UR5_PORT)
        self.socket_client.connect()
        self.command_generator = URScriptGenerator()
        # 初始 TCP (x, y, z, rx, ry, rz) 值，依實際初始位置設定
        self.initial_tcp = [0.279134293245, 0.045957778215, 0.218270318258, 2.216666768333, -2.213592243070, -0.007045821207]
        self.current_tcp = self.initial_tcp.copy()

    def compute_new_tcp(self, delta):
        new_tcp = self.current_tcp.copy()
        new_tcp[0] += delta[0]
        new_tcp[1] += delta[1]
        return new_tcp
    
    def handle_initial_command(self):
        ur_command = self.command_generator.initial_command()
        self.socket_client.send_command(ur_command)

    def handle_move_command(self, direction):
        # 定義移動步長
        step = self.command_generator.step
        # 依據方向計算 x, y 的位移增量
        if direction == "forward":
            delta = [step, 0, 0]
        elif direction == "backward":
            delta = [-step, 0, 0]
        elif direction == "left":
            delta = [0, step, 0]
        elif direction == "right":
            delta = [0, -step, 0]
        elif direction == "right_forward":
            diag = step / 1.414
            delta = [diag, -diag, 0]
        elif direction == "right_backward":
            diag = step / 1.414
            delta = [-diag, -diag, 0]
        elif direction == "left_forward":
            diag = step / 1.414
            delta = [diag, diag, 0]
        elif direction == "left_backward":
            diag = step / 1.414
            delta = [-diag, diag, 0]
        else:
            return "未知指令"

        new_tcp = self.compute_new_tcp(delta)
        # 若目標 TCP 超出邊界，則返回錯誤訊息
        if not is_within_boundaries(new_tcp):
            self.logger.warning("Target TCP {} out of boundaries".format(new_tcp))
            return "指令超出邊界，無法執行"

        self.current_tcp = new_tcp
        ur_command = self.command_generator.generate_move_command(direction)
        self.socket_client.send_command(ur_command)
        return "執行移動"

    def handle_command(self, cmd):
        if self.state != "idle" and cmd != "stop":
            self.logger.warning("State {} not idle, command {} rejected".format(self.state, cmd))
            return "當前忙碌中，請稍後再試"
        
        if cmd in ["forward", "backward", "left", "right", "right_forward", "right_backward", "left_forward", "left_backward"]:
            self.state = "moving"
            result = self.handle_move_command(cmd)
        elif cmd == "grab":
            self.state = "grabbing"
            rgdown_ur_command = self.command_generator.generate_grab_down_command()
            self.socket_client.send_command(rgdown_ur_command)
            sleep(2)
            RGGrab()
            sleep(2)
            rgup_ur_command = self.command_generator.generate_grab_up_command()
            self.socket_client.send_command(rgup_ur_command)
            sleep(2)
            Point_triangle()
            sleep(2)
            RGRelease()
            sleep(2)
            Point0()
            sleep(2)
            self.current_tcp = self.initial_tcp.copy()
            result = "執行抓取"
        elif cmd == "stop":
            self.state = "idle"
            ur_command = "stop"
            self.socket_client.send_command(ur_command)
            result = "停止操作"
        else:
            result = "未知命令"
        
        self.logger.info("Command {} processed with result: {}".format(cmd, result))
        self.state = "idle"
        return result
