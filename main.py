import os
import threading
import time
import socket
import re
from file_server import FileServer
from file_client import FileClient
from config_manager import ConfigManager

class FileTransferApp:
    def __init__(self):
        self.config = ConfigManager()
        self.server = FileServer()
        self.client = FileClient()
        self.server_running = False
        
    def _is_valid_ip(self, ip):
        """验证IP地址格式是否正确，支持可选的端口号"""
        # 分离IP和端口
        if ':' in ip:
            ip, port = ip.split(':')
            # 检查端口是否为有效数字且在范围内
            try:
                port = int(port)
                if not (0 < port < 65536):
                    return False
            except ValueError:
                return False
        
        # 验证IP地址格式
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
        # 检查每个数字是否在0-255范围内
        return all(0 <= int(num) <= 255 for num in ip.split('.'))
    
    def _get_local_ip(self):
        """获取本机IP地址"""
        try:
            # 创建一个UDP socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # 连接一个公网IP（不会真的建立连接）
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
    
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
                print(f"本机IP: {self._get_local_ip()}")
                print("1. 启动接收服务")
                print("2. 发送文件")
                print("3. 退出")
                choice = input("\n请选择操作 (1/2/3): ")
                
                if choice == "1":
                    self.start_server_thread()
                elif choice == "2":
                    while True:
                        target_ip = input("请输入目标IP地址 [可选端口号]: ")
                        if self._is_valid_ip(target_ip):
                            break
                        print("错误：无效的IP地址格式")
                        print("正确格式示例：")
                        print("  - 192.168.1.100")
                        print("  - 192.168.1.100:9999")
                    
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
                        try:
                            self.client.send_file(target_ip, filepath)
                        except ConnectionRefusedError:
                            print(f"错误：连接被拒绝，请确保目标计算机 ({target_ip}) 已启动接收服务")
                        except socket.timeout:
                            print(f"错误：连接超时，请检查目标IP是否正确，且在同一局域网内")
                        except Exception as e:
                            print(f"错误：{str(e)}")
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