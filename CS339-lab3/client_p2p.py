from socket import *
import optparse
import time
import random


def client(client_name, server_ip='127.0.0.1', server_port=12000):
    peer_port = 9999
    client_socket = [socket(AF_INET, SOCK_STREAM)]  # socket for server and tracker
    client_socket[0].connect((server_ip, server_port))
    client_socket[0].send('file length'.encode())
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', peer_port))
    server_socket.listen(6)
    blocks_num = int(client_socket[0].recv(1024).decode())
    print('blocks num:', blocks_num)
    blocks_needed = list(range(blocks_num))
    start_time = time.time()
    file_recv = ['' for _ in range(blocks_num)]
    file = open('recv/' + client_name + '_p2p.txt', 'w')
    peer_list = []  # name of peers already have link
    peer_sock_list = []
    collecting = True
    # getting file
    while len(blocks_needed) != 0:
        print('still need {} blocks'.format(len(blocks_needed)))
        random.shuffle(blocks_needed)
        client_socket[0].send(('file part'+str(blocks_needed[0])).encode())
        print('ask for', blocks_needed[0])
        block_recv = client_socket[0].recv(1024)
        if (blocks_needed[0] != blocks_num-1) and len(block_recv) != 1024:
            continue
        peers = client_socket[0].recv(1024).decode().split(',')
        time.sleep(0.2)
        peer_num = int(peers[0])
        del peers[0]
        print('peer num:', peer_num)
        if peer_num == 0:
            continue
        for i, peer_ip in list(enumerate(peers)):
            print('peer:', peer_ip)
            try:
                if collecting:
                    peer_list.append(peer_ip)
                    client_socket.append(socket(AF_INET, SOCK_STREAM))
                    client_socket[-1].connect((peer_ip, peer_port))
                client_socket[i+1].send(str(blocks_needed[0]).zfill(5).encode())
                client_socket[i+1].send(block_recv)
            except Exception as e:
                print(e)
            print('send', str(blocks_needed[0]).zfill(5), block_recv.decode()[:10], '...')
        file_recv[blocks_needed[0]] = block_recv.decode()
        del blocks_needed[0]
        if len(blocks_needed) == 0:
            time.sleep(1)
            break
        for i in range(peer_num):
            print('trying to receive from', peer_list[i])
            try:
                if collecting:
                    sock, addr = server_socket.accept()
                    peer_sock_list.append(sock)
                else:
                    sock = peer_sock_list[i]
                block_num = int(sock.recv(5).decode())
                time.sleep(0.1)
                block_recv = sock.recv(1024)
                print('receive', block_num, block_recv.decode()[:10], '...')
                if (block_num != blocks_num-1) and len(block_recv) != 1024:
                    continue
                file_recv[block_num] = block_recv.decode()
                if block_num in blocks_needed:
                    blocks_needed.remove(block_num)
            except Exception as e:
                print(e)
        collecting = False
        # print('set collecting true')
    # store the file
    print('receive done!')
    file_recv = ''.join(file_recv)
    file.write(file_recv)
    # send downloading time
    download_time = time.time() - start_time
    client_socket[0].send(('time consumed ' + str(download_time)).encode())
    time.sleep(5)
    for s in client_socket:
        s.close()


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-n', dest='name', type=str)
    parser.add_option('-i', dest='ip', type=str)
    parser.add_option('-p', dest='port', type=int)
    (opt, args) = parser.parse_args()
    print(opt, args)
    client(opt.name, opt.ip, opt.port)
