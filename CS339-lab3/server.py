from socket import *
import time
import threading

start_time = 0  # time that tcp link starts


def tcpLink(sock, addr):
    global start_time
    if start_time == 0:  # means it's the first time tcp
        start_time = time.time()
    print('Accept new connection from %s:%s...' % addr)
    file = open('data.txt', 'r')
    send = file.read().encode()
    send_len = len(send)
    sock.send(str(send_len).encode())
    data = sock.recv(1024).decode()
    if data == 'request for file':
        sock.send(send)
    data = sock.recv(1024).decode()  # time of receiving data
    print('{} seconds past before {} receives data'.format(float(data)-start_time, addr))
    sock.close()
    print('Connection from %s:%s closed.' % addr)


def server():
    server_port = 12000
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', server_port))
    server_socket.listen(6)
    print('server ready')
    time.sleep(1)
    while True:
        sock, addr = server_socket.accept()
        t = threading.Thread(target=tcpLink, args=(sock, addr))
        t.start()


if __name__ == '__main__':
    server()
