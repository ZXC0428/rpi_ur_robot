import socket
import threading
import time
import logging

class SocketClient:
    def __init__(self, host, port, timeout=5):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None
        self.lock = threading.Lock()  # 確保線程安全
        self.logger = logging.getLogger("SocketClient")
        self.connected = False

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            self.connected = True
            self.logger.info("Connected to {}:{}".format(self.host, self.port))
        except Exception as e:
            self.logger.error("Connection error: {}".format(e))
            self.connected = False

    def send_command(self, command):
        if not self.connected:
            self.connect()
        try:
            with self.lock:
                self.socket.sendall(command.encode('utf-8'))
                # self.logger.info("Sent command: {}".format(command))
        except Exception as e:
            self.logger.error("Send command error: {}".format(e))
            self.connected = False

    def receive_response(self):
        try:
            with self.lock:
                data = self.socket.recv(1024)
                response = data.decode('utf-8')
                self.logger.info("Received response: {}".format(response))
                return response
        except Exception as e:
            self.logger.error("Receive error: {}".format(e))
            self.connected = False
            return None

    def close(self):
        if self.socket:
            self.socket.close()
            self.connected = False
            self.logger.info("Connection closed")
