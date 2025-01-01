import socket
import os
import zipfile
from tqdm import tqdm
from config_manager import ConfigManager

class FileServer:
    def __init__(self):
        self.config = ConfigManager()
        self.host = self.config.get('network', 'host')
        self.port = self.config.get('network', 'port')
        self.buffer_size = self.config.get('network', 'buffer_size')
        self.max_file_size = self.config.get('file', 'max_size')
        self.save_path = self.config.get('file', 'save_path')
        
        # 确保保存目录存在
        os.makedirs(self.save_path, exist_ok=True)
        
    def start_listening(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"等待连接中... (端口: {self.port})")
        
        server_socket.settimeout(self.config.get('network', 'timeout'))
        
        try:
            while True:
                try:
                    client_socket, address = server_socket.accept()
                    print(f"收到来自 {address} 的连接")
                    self.handle_client(client_socket)
                except socket.timeout:
                    continue
                except KeyboardInterrupt:
                    raise
        except KeyboardInterrupt:
            print("\n接收服务停止")
        finally:
            server_socket.close()
    
    def handle_client(self, client_socket):
        try:
            # 参数协商
            # 接收客户端的 buffer_size
            client_buffer_size = int(client_socket.recv(1024).decode())
            # 发送服务器的 buffer_size
            client_socket.send(str(self.buffer_size).encode())
            # 使用较小的值作为实际的 buffer_size
            self.buffer_size = min(self.buffer_size, client_buffer_size)
            print(f"协商的缓冲区大小: {self.buffer_size} 字节/次")
            
            # 接收文件信息
            info = client_socket.recv(1024).decode()
            filename, is_dir = info.split('|')
            is_dir = bool(int(is_dir))
            client_socket.send("ok".encode())
            
            # 接收文件大小并检查
            filesize = int(client_socket.recv(1024).decode())
            if filesize > self.max_file_size:
                print(f"\n警告：文件大小 ({self._format_size(filesize)}) 超过设定值 ({self._format_size(self.max_file_size)})")
                choice = input("是否继续接收？(y/n): ").lower()
                if choice != 'y':
                    client_socket.send(f"error:文件过大，服务器拒绝接收".encode())
                    return
                print("继续接收文件...")
            client_socket.send("ok".encode())
            
            # 接收文件内容
            progress = tqdm(range(filesize), f"接收 {filename}", 
                          unit="B", unit_scale=True, unit_divisor=1024)
            
            with open(filename, "wb") as f:
                bytes_received = 0
                while bytes_received < filesize:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    f.write(data)
                    bytes_received += len(data)
                    progress.update(len(data))
            
            print(f"\n文件 {filename} 接收完成")
            
            # 如果是文件夹，解压缩
            if is_dir:
                try:
                    print("正在解压文件...")
                    extract_dir = os.path.splitext(filename)[0]
                    with zipfile.ZipFile(filename, 'r') as zipf:
                        zipf.extractall(extract_dir)
                    os.remove(filename)  # 删除zip文件
                    print(f"文件夹已解压到: {extract_dir}")
                except Exception as e:
                    print(f"解压文件时出错: {e}")
            
        except Exception as e:
            print(f"接收文件时出错: {e}")
        finally:
            client_socket.close() 
    
    def _format_size(self, size):
        """将字节大小转换为人类可读的格式"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}PB" 