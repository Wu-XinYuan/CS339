from socket import *
import optparse
import time
import random


def client(client_name, server_ip='127.0.0.1'):
    server_port = 12000
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((server_ip, server_port))
    client_socket.send('file length'.encode())
    blocks_num = int(client_socket.recv(1024).decode())
    blocks_needed = list(range(blocks_num))
    start_time = time.time()
    file_recv = [''for _ in range(blocks_num)]
    file = open('recv/'+client_name+'.txt', 'w')
    while len(blocks_needed) != 0:
        random.shuffle(blocks_needed)


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-n', dest='name', type=str)
    parser.add_option('-i', dest='ip', type=str)
    (opt, args) = parser.parse_args()
    print(opt, args)
    client(opt.name, opt.ip)
