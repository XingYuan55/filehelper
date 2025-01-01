import socket
import os
import zipfile
import tempfile
from tqdm import tqdm
from config_manager import ConfigManager

class FileClient:
    def __init__(self):
        self.config = ConfigManager()
        self.port = self.config.get('network', 'port')
        self.buffer_size = self.config.get('network', 'buffer_size')
        self.max_file_size = self.config.get('file', 'max_size')
        self.compress_level = self.config.get('transfer', 'compress_level')
        
    def _format_size(self, size):
        """将字节大小转换为人类可读的格式"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}PB"

    def send_file(self, target_ip, filepath):
        try:
            # 检查路径是否存在
            if not os.path.exists(filepath):
                print("错误：文件或文件夹不存在！")
                return

            # 如果是文件夹，先压缩
            is_dir = os.path.isdir(filepath)
            if is_dir:
                print("检测到文件夹，正在压缩...")
                filepath = self._compress_directory(filepath)
                if not filepath:
                    return
            
            # 检查文件大小
            filesize = os.path.getsize(filepath)
            if filesize > self.max_file_size:
                print(f"错误：文件过大！最大支持 {self._format_size(self.max_file_size)}")
                return
            
            # 连接到服务器
            print("连接到服务器...")
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((target_ip, self.port))
            
            # 参数协商
            # 发送本地 buffer_size
            client_socket.send(str(self.buffer_size).encode())
            # 接收服务器的 buffer_size
            server_buffer_size = int(client_socket.recv(1024).decode())
            # 使用较小的值作为实际的 buffer_size
            self.buffer_size = min(self.buffer_size, server_buffer_size)
            print(f"协商的缓冲区大小: {self._format_size(self.buffer_size)}/次")
            
            # 发送文件信息
            filename = os.path.basename(filepath)
            if is_dir:
                # 如果是压缩后的文件夹，添加.zip后缀
                filename = os.path.splitext(filename)[0] + ".zip"
            
            # 发送文件名和是否为文件夹的标志
            info = f"{filename}|{1 if is_dir else 0}"
            client_socket.send(info.encode())
            client_socket.recv(1024)  # 等待确认
            
            # 发送文件大小
            client_socket.send(str(filesize).encode())
            response = client_socket.recv(1024).decode()
            if response.startswith("error:"):
                print(f"服务器拒绝接收：{response[6:]}")
                return
            
            # 发送文件内容
            progress = tqdm(range(filesize), f"发送 {filename}", 
                          unit="B", unit_scale=True, unit_divisor=1024)
            
            with open(filepath, "rb") as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    client_socket.send(data)
                    progress.update(len(data))
            
            print(f"\n文件 {filename} 发送完成")
            
        except Exception as e:
            print(f"发送文件时出错: {e}")
        finally:
            client_socket.close() 