import socket
import os
from tqdm import tqdm

class FileServer:
    def __init__(self, host='0.0.0.0', port=9999):
        self.host = host
        self.port = port
        
    def start_listening(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"等待连接中... (端口: {self.port})")
        
        try:
            while True:
                client_socket, address = server_socket.accept()
                print(f"收到来自 {address} 的连接")
                self.handle_client(client_socket)
        except KeyboardInterrupt:
            print("\n服务器已停止")
        finally:
            server_socket.close()
    
    def handle_client(self, client_socket):
        try:
            # 接收文件名
            filename = client_socket.recv(1024).decode()
            client_socket.send("ok".encode())
            
            # 接收文件大小
            filesize = int(client_socket.recv(1024).decode())
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
            
        except Exception as e:
            print(f"接收文件时出错: {e}")
        finally:
            client_socket.close() 