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
    
    def _normalize_path(self, filepath):
        """智能处理文件路径"""
        # 处理用户输入的路径（处理引号）
        filepath = filepath.strip('"\'')
        # 将反斜杠转换为正斜杠
        filepath = filepath.replace('\\', '/')
        
        # 判断是否是绝对路径
        is_absolute = os.path.isabs(filepath)
        
        # 获取规范化的路径
        if is_absolute:
            normalized_path = os.path.normpath(filepath)
            print(f"检测到绝对路径: {normalized_path}")
        else:
            # 相对路径转换为绝对路径
            abs_path = os.path.abspath(filepath)
            print(f"检测到相对路径，转换为: {abs_path}")
            normalized_path = abs_path
            
        return normalized_path
        
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
                    print("\n提示：")
                    print("- 可以直接拖拽文件/文件夹到窗口中")
                    print("- 支持绝对路径 (如 C:/folder/file.txt)")
                    print("- 支持相对路径 (如 ./folder/file.txt)")
                    print('- Windows系统可以右键文件/文件夹，选择"复制为路径"')
                    filepath = input("请输入要发送的文件路径: ")
                    
                    # 处理文件路径
                    filepath = self._normalize_path(filepath)
                    
                    if os.path.exists(filepath):
                        print(f"正在发送: {filepath}")
                        self.client.send_file(target_ip, filepath)
                    else:
                        print(f"错误：找不到文件或文件夹：{filepath}")
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