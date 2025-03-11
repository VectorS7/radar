import socket
import threading
import queue
import os

class StreamingServer:
    def __init__(self, host="0.0.0.0", port=int(os.getenv("PORT", 5000))):
        self.host = host
        self.port = port
        self.clients = []
        self.buffer = queue.Queue()
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        
        # Порт для HTTP раздачи (на 1 больше)
        self.broadcast_port = self.port + 1
        self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.broadcast_socket.bind((self.host, self.broadcast_port))
        self.broadcast_socket.listen(10)

    def accept_source(self):
        while True:
            print(f"Ожидаю источник на {self.host}:{self.port}")
            conn, addr = self.server_socket.accept()
            print(f"Подключен источник: {addr}")
            conn.settimeout(5.0)
            while True:
                try:
                    data = conn.recv(4096)
                    if not data:
                        print(f"Источник {addr} отключился")
                        break
                    self.buffer.put(data)
                except socket.timeout:
                    continue
            conn.close()

    def handle_client(self, client_socket, request):
        print("Новый клиент подключен")
        if b"GET /stream" in request:
            header = "HTTP/1.0 200 OK\r\nContent-Type: audio/flac\r\n\r\n".encode()
            client_socket.sendall(header)
            while True:
                try:
                    data = self.buffer.get()
                    client_socket.sendall(data)
                except:
                    client_socket.close()
                    break
        else:
            html_page = (
                "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n"
                "<!DOCTYPE html><html><head><title>Audio Stream</title></head>"
                "<body><h1>Live Audio Stream</h1>"
                "<audio controls autoplay><source src='/stream' type='audio/flac'>"
                "Your browser does not support the audio element.</audio></body></html>"
            ).encode()
            client_socket.sendall(html_page)
            client_socket.close()

    def accept_clients(self):
        print(f"HTTP сервер на {self.host}:{self.broadcast_port}")
        while True:
            client_socket, addr = self.broadcast_socket.accept()
            request = client_socket.recv(1024)
            threading.Thread(target=self.handle_client, 
                           args=(client_socket, request), 
                           daemon=True).start()

    def start(self):
        source_thread = threading.Thread(target=self.accept_source, daemon=True)
        clients_thread = threading.Thread(target=self.accept_clients, daemon=True)
        source_thread.start()
        clients_thread.start()
        source_thread.join()
        clients_thread.join()

if __name__ == "__main__":
    server = StreamingServer()
    server.start()
