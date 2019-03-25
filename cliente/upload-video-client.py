import socket
import sys
IP = '192.168.0.6'
PORT = 65432

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))

if len(sys.argv) != 2:
    print("usage:", sys.argv[0], "<video path>")
    sys.exit(1)

with open(sys.argv[1], 'rb') as f:
    data = f.read()
    s.sendall(data)
s.shutdown(socket.SHUT_RDWR)
s.close()
