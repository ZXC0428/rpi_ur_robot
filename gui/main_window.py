# import sys
# from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QWidget, QGridLayout
# from control.state_machine import ControlModule
# from control.get_position import get_current_tcp_joint_positions
# from datetime import datetime

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("夾娃娃機控制介面")
#         self.control_module = ControlModule()
#         self.init_ui()

#     def init_ui(self):
#         central_widget = QWidget()
#         grid = QGridLayout()

#         # 新增方向按鈕，排列成 3×3 格局：
#         # 第一列：左前、前、右前
#         self.btn_left_forward = QPushButton("左前")
#         self.btn_forward = QPushButton("前")
#         self.btn_right_forward = QPushButton("右前")
#         # 第二列：左、右（中間留空）
#         self.btn_left = QPushButton("左")
#         self.btn_right = QPushButton("右")
#         # 第三列：左後、後、右後
#         self.btn_left_backward = QPushButton("左後")
#         self.btn_backward = QPushButton("後")
#         self.btn_right_backward = QPushButton("右後")
#         # 抓取按鈕放置在第四列中間
#         self.btn_grab = QPushButton("抓取")

#         grid.addWidget(self.btn_left_forward, 0, 0)
#         grid.addWidget(self.btn_forward, 0, 1)
#         grid.addWidget(self.btn_right_forward, 0, 2)
#         grid.addWidget(self.btn_left, 1, 0)
#         grid.addWidget(self.btn_right, 1, 2)
#         grid.addWidget(self.btn_left_backward, 2, 0)
#         grid.addWidget(self.btn_backward, 2, 1)
#         grid.addWidget(self.btn_right_backward, 2, 2)
#         grid.addWidget(self.btn_grab, 3, 1)

#         # 狀態訊息顯示區放在最下方
#         self.status_label = QLabel("系統初始化中...")
#         self.control_module.handle_initial_command()
#         grid.addWidget(self.status_label, 4, 0, 1, 3)

#         central_widget.setLayout(grid)
#         self.setCentralWidget(central_widget)

#         # 各方向按鈕皆以單次點擊事件觸發對應指令
#         self.btn_left_forward.clicked.connect(lambda: self.send_command("left_forward"))
#         self.btn_forward.clicked.connect(lambda: self.send_command("forward"))
#         self.btn_right_forward.clicked.connect(lambda: self.send_command("right_forward"))
#         self.btn_left.clicked.connect(lambda: self.send_command("left"))
#         self.btn_right.clicked.connect(lambda: self.send_command("right"))
#         self.btn_left_backward.clicked.connect(lambda: self.send_command("left_backward"))
#         self.btn_backward.clicked.connect(lambda: self.send_command("backward"))
#         self.btn_right_backward.clicked.connect(lambda: self.send_command("right_backward"))

#         # 抓取按鈕單次觸發
#         self.btn_grab.clicked.connect(lambda: self.send_command("grab"))

#     def send_command(self, cmd):
#         # 方向命令使用 handle_move_command，其他命令則使用 handle_command
#         if cmd in ["forward", "backward", "left", "right",
#                    "left_forward", "right_forward", "left_backward", "right_backward"]:
#             result = self.control_module.handle_move_command(cmd)

#             # 取得當前手臂位置
#             current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             tcp_pose, joint_positions = get_current_tcp_joint_positions()
#             print(f"Current Time: {current_time}\ntcp_pose={tcp_pose}\noint_positions={joint_positions}\n")
#         else:
#             result = self.control_module.handle_command(cmd)

#         self.status_label.setText(result)

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel,
    QWidget, QGridLayout
)
from PyQt5.QtCore import QTimer
from control.state_machine import ControlModule
from control.get_position import get_current_tcp_joint_positions
from control.get_state import get_robot_mode
from control.led_control import control_led, cleanup_led
from datetime import datetime

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("夾娃娃機控制介面")
        self.control_module = ControlModule()

        # 定時更新機台狀態
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_robot_status)
        self.status_timer.start(2000)  # 每秒更新一次

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        grid = QGridLayout()

        # 3×3 方向按鈕
        self.btn_left_forward = QPushButton("左前")
        self.btn_forward = QPushButton("前")
        self.btn_right_forward = QPushButton("右前")
        self.btn_left  = QPushButton("左")
        self.btn_right = QPushButton("右")
        self.btn_left_backward = QPushButton("左後")
        self.btn_backward  = QPushButton("後")
        self.btn_right_backward= QPushButton("右後")
        self.btn_grab = QPushButton("抓取")

        grid.addWidget(self.btn_left_forward, 0, 0)
        grid.addWidget(self.btn_forward, 0, 1)
        grid.addWidget(self.btn_right_forward,0, 2)
        grid.addWidget(self.btn_left, 1, 0)
        grid.addWidget(self.btn_right, 1, 2)
        grid.addWidget(self.btn_left_backward, 2, 0)
        grid.addWidget(self.btn_backward, 2, 1)
        grid.addWidget(self.btn_right_backward, 2, 2)
        grid.addWidget(self.btn_grab, 3, 1)

        # 操作回饋狀態
        self.status_label = QLabel("系統初始化中...")
        grid.addWidget(self.status_label, 4, 0, 1, 3)

        # 機台運行模式顯示
        self.mode_label = QLabel("運行模式：讀取中…")
        grid.addWidget(self.mode_label, 5, 0, 1, 3)

        central_widget.setLayout(grid)
        self.setCentralWidget(central_widget)

        # 綁定按鈕
        self.btn_left_forward.clicked.connect(lambda: self.send_command("left_forward"))
        self.btn_forward.clicked.connect(lambda: self.send_command("forward"))
        self.btn_right_forward.clicked.connect(lambda: self.send_command("right_forward"))
        self.btn_left.clicked.connect(lambda: self.send_command("left"))
        self.btn_right.clicked.connect(lambda: self.send_command("right"))
        self.btn_left_backward.clicked.connect(lambda: self.send_command("left_backward"))
        self.btn_backward.clicked.connect(lambda: self.send_command("backward"))
        self.btn_right_backward.clicked.connect(lambda: self.send_command("right_backward"))
        self.btn_grab.clicked.connect(lambda: self.send_command("grab"))

        # 初始化一次模式顯示
        self.update_robot_status()

    def update_robot_status(self):
        mode = get_robot_mode()
        mode_map = {
            'Disconnected': '已斷線',
            'Confirm Safety': '等待安全確認',
            'Booting': '開機中',
            'Power Off': '關閉電源',
            'Power On': '開啟電源',
            'Idle': '待機',
            'Backdrive': '回動',
            'Running': '運行中',
            'Updating Firmware': '韌體更新'
        }
        if mode:
            text = mode_map.get(mode, mode)
            self.mode_label.setText(f"運行模式：{text}")
            if text == '關閉電源':
                control_led(11, 'on')
                control_led(12, 'off')
                control_led(13, 'off')
            if text == '運行中':
                control_led(12, 'on')
                control_led(11, 'off')
                control_led(13, 'off')
            if text == '待機':
                control_led(13, 'on')
                control_led(12, 'off')
                control_led(11, 'off')

        else:
            self.mode_label.setText("運行模式：讀取失敗")

    def send_command(self, cmd):
        # 如果是移動，就呼叫 handle_move_command
        if cmd in ["forward", "backward", "left", "right",
                   "left_forward", "right_forward", "left_backward", "right_backward"]:
            result = self.control_module.handle_move_command(cmd)
            # 同步取得當前位姿（可選）
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            tcp_pose, joint_positions = get_current_tcp_joint_positions()
            print(f"{current_time}\nTCP:{tcp_pose}\n關節:{joint_positions}\n")
        else:
            result = self.control_module.handle_command(cmd)

        self.status_label.setText(result)

if __name__ == "__main__":
    cleanup_led()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
