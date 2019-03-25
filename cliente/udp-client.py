import socket
import struct
import sys
import threading
import time
import cv2
import numpy as np

if len(sys.argv) != 3:
    print("usage:", sys.argv[0], "<multicast_group> <port>")
    sys.exit(1)

multicast_group = sys.argv[1]
server_address = ('', int(sys.argv[2]))
header = False

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind to the server address
sock.bind(server_address)

# Tell the operating system to add the socket to
# the multicast group on all interfaces.
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(
    socket.IPPROTO_IP,
    socket.IP_ADD_MEMBERSHIP,
    mreq)

def show(data):
    cv2.imshow('Streaming', cv2.imdecode(np.asarray(bytearray(data), dtype=np.uint8), 1))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()

# Receive/respond loop
while True:
    data, address = sock.recvfrom(65535)
    show(data)