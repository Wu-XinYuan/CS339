from socket import *
import time


def server():
    server_port = 12000
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', server_port))
    server_socket.listen(6)
    print('server ready')
    time.sleep(1)
    file = open('data.txt', 'r')
    file = file.read().encode()
    file_blocks = [file[i:i+1024] for i in range(0, len(file), 1024)]  # cut the file to be delivered into blocks
    while True:
        sock, addr = server_socket.accept()
        recv = sock.recv(1024).decode()  # request
        if recv == 'file length':
            sock.send(str(len(file_blocks)).encode())
        elif recv == 'file part':  # if requesting for part of the file, then listen for which part then send
            part = int(sock.recv(1024).decode())
            sock.send(file_blocks[part])
        elif recv == 'time consumed':
            t = float(sock.recv(1024).decode())
            print('{} secs before {} finish downloading'.format(t, addr))


if __name__ == '__main__':
    server()
