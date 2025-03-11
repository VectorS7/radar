import pyaudio
import pyflac
import socket
import numpy as np
import time

class AudioStreamer:
    def __init__(self, server_host="radar.zone.id", server_port=5000):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2
        self.RATE = 44100
        self.server_host = server_host
        self.server_port = server_port
        
        self.p = pyaudio.PyAudio()
        try:
            self.stream = self.p.open(format=self.FORMAT,
                                    channels=self.CHANNELS,
                                    rate=self.RATE,
                                    input=True,
                                    frames_per_buffer=self.CHUNK)
            print("Аудиоустройство открыто")
        except Exception as e:
            print(f"Ошибка аудио: {e}")
            self.p.terminate()
            raise
        
        self.sock = None
        self.encoder = None
        self.connect_to_server()

    def connect_to_server(self):
        if self.sock:
            self.sock.close()
        if self.encoder:
            self.encoder.finish()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.sock.connect((self.server_host, self.server_port))
                print("Успешно подключено к серверу")
                break
            except Exception as e:
                print(f"Ошибка подключения к серверу: {e}, повтор через 2 секунды...")
                time.sleep(2)
        
        self.encoder = pyflac.StreamEncoder(sample_rate=self.RATE, 
                                          write_callback=self.write_callback)
        self.encoder.channels = self.CHANNELS
        self.encoder.bits_per_sample = 16

    def write_callback(self, buffer, num_bytes, num_samples, current_frame):
        if num_bytes > 0:
            try:
                self.sock.sendall(buffer)
            except Exception as e:
                print(f"Ошибка отправки: {e}")
                raise

    def stream_audio(self):
        print("Начинаю трансляцию...")
        while True:
            try:
                data = self.stream.read(self.CHUNK)
                pcm_data = np.frombuffer(data, dtype=np.int16)
                self.encoder.process(pcm_data)
            except Exception as e:
                print(f"Ошибка в потоке: {e}")
                self.connect_to_server()
    
    def cleanup(self):
        if self.encoder:
            self.encoder.finish()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        if self.sock:
            self.sock.close()

if __name__ == "__main__":
    streamer = None
    try:
        streamer = AudioStreamer("radar.zone.id", 5000)
        streamer.stream_audio()
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if streamer is not None:
            streamer.cleanup()
