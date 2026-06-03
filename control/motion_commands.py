import math

class URScriptGenerator:
    def __init__(self):
        # 固定參數，可根據需求調整
        self.fixed_height = 0.2    # 固定高度 (公尺)
        self.step = 0.02           # 每次移動步長 (公尺)
        self.speed = 0.25          # 移動速度
        self.acceleration = 1.1    # 加速度

    def initial_command(self):
        command = "movej(get_inverse_kin(p[.279134293245, .045957778215, .218270318258, 2.216666768333, -2.213592243070, -.007045821207], qnear=[0.5594176650047302, -1.0216768423663538, -2.0281041304217737, -1.6719406286822718, 1.5753320455551147, -2.5834994951831263]), a=1.3962634015954636, v=1.0471975511965976)\n"
        return command

    def generate_move_command(self, direction):
        """
        依據方向產生水平移動的 URScript 指令
        """
        if direction == "forward":
            delta = [self.step, 0, 0]
        elif direction == "backward":
            delta = [-self.step, 0, 0]
        elif direction == "left":
            delta = [0, -self.step, 0]
        elif direction == "right":
            delta = [0, self.step, 0]
        elif direction == "left_forward":
            diag = self.step / math.sqrt(2)
            delta = [diag, -diag, 0]
        elif direction == "right_forward":
            diag = self.step / math.sqrt(2)
            delta = [diag, diag, 0]
        elif direction == "left_backward":
            diag = self.step / math.sqrt(2)
            delta = [-diag, -diag, 0]
        elif direction == "right_backward":
            diag = self.step / math.sqrt(2)
            delta = [-diag, diag, 0]
        else:
            delta = [0, 0, 0]
        
        # 組合 URScript 指令 (以 movel 為例)
        command = f"""
        movel(pose_trans(get_actual_tcp_pose(), p[{delta[0]}, {delta[1]}, {delta[2]}, 0, 0, 0]), {self.acceleration}, {self.speed})
        """
        return command


    def generate_grab_down_command(self):
        """
        生成抓取動作的 URScript 指令：下降
        """
        command = f"""
        movel(pose_trans(get_actual_tcp_pose(), p[0, 0, 0.15, 0, 0, 0]), {self.acceleration}, {self.speed})
        """
        return command

    def generate_grab_up_command(self):
        """
        生成抓取動作的 URScript 指令組合：上升
        """
        command = f"""
        movel(pose_trans(get_actual_tcp_pose(), p[0, 0, -0.1, 0, 0, 0]), {self.acceleration}, {self.speed})
        """
        return command
