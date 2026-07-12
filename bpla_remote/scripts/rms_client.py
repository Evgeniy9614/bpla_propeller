#!/usr/bin/env python3
import socket, sys

class RMSClient:
    def __init__(self, host="localhost", port=8080):
        self.host, self.port = host, port
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        print(f"Connected to {self.host}:{self.port}")
    def send(self, cmd):
        self.sock.send((cmd+"\n").encode())
        return self.sock.recv(1024).decode().strip()
    def close(self): self.sock.close()
    def run(self):
        print("Commands: TAKEOFF, LAND, RPM [val], STATUS, QUIT")
        while True:
            try:
                c = input("RMS> ").strip().upper()
                if c == "QUIT": break
                if c: print(self.send(c))
            except KeyboardInterrupt: break

if __name__ == "__main__":
    c = RMSClient()
    c.connect()
    c.run()
    c.close()
