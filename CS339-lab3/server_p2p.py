from socket import *
import time


def server():
    clients_num = 6
    server_port = 12000
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', server_port))
    server_socket.listen(6)
    print('server ready')
    time.sleep(1)
    sock_list = []
    client_list = []
    file = open('data.txt', 'r')
    file = file.read().encode()
    file_blocks = [file[i:i + 1024] for i in range(0, len(file), 1024)]  # cut the file to be delivered into blocks
    collecting = True
    i = -1
    while True:
        if collecting and len(client_list) < 6:
            sock, addr = server_socket.accept()
            print('Accept new connection from %s:%s...' % addr)
            sock_list.append(sock)
            client_list.append(addr[0])
            addr = addr[0]
        else:
            collecting = False
            i = (i + 1) % len(sock_list)
            sock = sock_list[i]
            addr = client_list[i]
        try:
            recv = sock.recv(1024).decode()  # request
        except Exception as e:
            print(e)
            continue
        if recv == 'file length':
            sock.send(str(len(file_blocks)).encode())
        elif recv.startswith('file part'):  # if requesting for part of the file, then listen for which part then send
            part = int(recv[9:])
            print('going to send', part)
            sock.send(file_blocks[part])
            list_tmp = [ip for ip in client_list if ip != addr]
            sock.send((str(len(list_tmp))+','+','.join(list_tmp)).encode())
        elif recv.startswith('time consumed'):
            t = float(recv[15:])
            print('{} secs before {} finish downloading'.format(t, addr))
        time.sleep(0.1)


if __name__ == '__main__':
    server()
