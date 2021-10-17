from socket import *
import optparse
import time


def client(client_name, server_ip='127.0.0.1'):
    server_port = 12000
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((server_ip, server_port))
    total_len = int(client_socket.recv(1024).decode())
    recv_len = 0
    sentence = 'request for file'.encode()
    client_socket.send(sentence)
    file = open('recv/'+client_name+'.txt', 'w')
    while recv_len != total_len:
        recv = client_socket.recv(1024)
        recv_len += len(recv)
        file.write(recv.decode())
    recv_time = time.time()
    # print('client{} receive message:{}'.format(client_name, recv.decode()))
    client_socket.send(str(recv_time).encode())
    client_socket.close()


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-n', dest='name', type=str)
    parser.add_option('-i', dest='ip', type=str)
    (opt, args) = parser.parse_args()
    print(opt, args)
    client(opt.name, opt.ip)
