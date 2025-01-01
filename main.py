import os
import threading
import time
from file_server import FileServer
from file_client import FileClient
from config_manager import ConfigManager

class FileTransferApp:
    def __init__(self):
        self.config = ConfigManager()
        self.server = FileServer()
        self.client = FileClient()
        self.server_running = False
        
    def start_server_thread(self):
        if not self.server_running:
            self.server_running = True
            print("\n接收服务已启动，等待文件传输...")
            print("(提示: 按 Ctrl+C 返回主菜单)")
            try:
                # 直接在主线程中运行服务器
                self.server.start_listening()
            except KeyboardInterrupt:
                print("\n\n停止接收服务，返回主菜单...")
            finally:
                self.server_running = False
        else:
            print("\n接收服务已经在运行中...")
        
    def show_menu(self):
        while True:
            try:
                print("\n=== 文件传输程序 ===")
                print("1. 启动接收服务")
                print("2. 发送文件")
                print("3. 退出")
                choice = input("\n请选择操作 (1/2/3): ")
                
                if choice == "1":
                    self.start_server_thread()
                elif choice == "2":
                    target_ip = input("请输入目标IP地址: ")
                    filepath = input("请输入要发送的文件路径: ")
                    if os.path.exists(filepath):
                        self.client.send_file(target_ip, filepath)
                    else:
                        print("文件不存在！")
                elif choice == "3":
                    print("\n程序已退出")
                    break
                else:
                    print("无效的选择！")
                    
            except KeyboardInterrupt:
                print("\n\n程序已退出")
                break

if __name__ == "__main__":
    app = FileTransferApp()
    app.show_menu() 