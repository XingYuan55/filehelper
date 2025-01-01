import socket
import os
from tqdm import tqdm

class FileClient:
    def __init__(self, port=9999):
        self.port = port
        
    def send_file(self, target_ip, filepath):
        try:
            # 连接到服务器
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((target_ip, self.port))
            
            # 获取文件名和大小
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)
            
            # 发送文件名
            client_socket.send(filename.encode())
            client_socket.recv(1024)  # 等待确认
            
            # 发送文件大小
            client_socket.send(str(filesize).encode())
            client_socket.recv(1024)  # 等待确认
            
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