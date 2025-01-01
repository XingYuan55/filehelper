import os
import threading
from file_server import FileServer
from file_client import FileClient

class FileTransferApp:
    def __init__(self, port=9999):
        self.port = port
        self.server = FileServer(port=port)
        self.client = FileClient(port=port)
        self.server_running = False
        
    def start_server_thread(self):
        if not self.server_running:
            server_thread = threading.Thread(target=self.server.start_listening)
            server_thread.daemon = True
            server_thread.start()
            self.server_running = True
            print("\n接收服务已启动，等待文件传输...")
            print("(提示: 可以按 Ctrl+C 停止接收服务)")
        else:
            print("\n接收服务已经在运行中...")
        
    def show_menu(self):
        while True:
            try:
                print("\n=== 文件传输程序 ===")
                if not self.server_running:
                    print("1. 启动接收服务")
                else:
                    print("1. 接收服务运行中")
                print("2. 发送文件")
                print("3. 退出")
                choice = input("\n请选择操作 (1/2/3): ")
                
                if choice == "1":
                    self.start_server_thread()
                elif choice == "2":
                    if self.server_running:
                        print("\n警告：当前正在接收文件，建议在新开一个程序窗口发送文件")
                        if input("是否继续? (y/n): ").lower() != 'y':
                            continue
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