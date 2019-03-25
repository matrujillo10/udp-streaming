import socket
import struct
import threading
import time
import cv2

HOST = '127.0.0.1'
PORT = 65432
MAX_BYTES = 1024
LAST_PORT = 65535
FIRST_PORT = 49152
last_multicasting_ip = '224.3.0.0'
last_multicasting_port = 49152
VIDEOS_DIR = '/home/alvaro/'
filename_template = 'recv_${}.mp4'
curr_filename = 0

def start_streaming(path, multicast_group):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ttl = struct.pack('b', 1)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    stream(s, multicast_group, path)

def new_multicast_group():
    global last_multicasting_ip, last_multicasting_port
    if last_multicasting_port < LAST_PORT:
        last_multicasting_port += 1
        return (last_multicasting_ip, last_multicasting_port)
    nums = [int(i) for i in last_multicasting_ip.split('.')]
    if nums[-1] < 255:
        nums[-1] += 1
    elif nums[-2] < 255:
        nums[-2] += 1
        nums[-1] = 0
    elif nums[-3] < 4:
        nums[-3] += 1
        nums[-2] = 0
        nums[-1] = 0
    else:
        raise Exception('IPs for multicasting groups exceeded')
    last_multicasting_ip, last_multicasting_port = ('.'.join([str(i) for i in nums]), FIRST_PORT)
    return (last_multicasting_ip, last_multicasting_port)

def stream(sock, multicast_group, filename):
    while True:
        video = cv2.VideoCapture(filename)
        while video.isOpened():
            success, image = video.read()
            if not success:
                break
            ret, jpeg = cv2.imencode('.jpg', image)
            if not ret:
                break
            sock.sendto(jpeg.tobytes(), multicast_group)
            time.sleep(0.05)

def resolve(conn, addr):
    global filename_template, curr_filename
    data = conn.recv(MAX_BYTES)
    path = VIDEOS_DIR+filename_template.replace('${}', str(curr_filename))
    curr_filename += 1
    f = open(path, 'wb')
    while data:
        f.write(data)
        data = conn.recv(MAX_BYTES)
    conn.close()
    start_streaming(path, new_multicast_group())

tcp_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_s.bind((HOST, PORT))
tcp_s.listen()
while True:
    conn, addr = tcp_s.accept()
    threading.Thread(target=resolve, args=(conn,addr)).start()
