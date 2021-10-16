import threading
import time

from server import server
from client import client


if __name__ == '__main__':
    server_thread = threading.Thread(target=server)
    client_num = 6
    client_threads = []
    for i in range(client_num):
        client_threads.append(threading.Thread(target=client, args=(str(i),)))
    server_thread.start()
    time.sleep(1)
    for i in range(client_num):
        client_threads[i].start()
    server_thread.join()
    for i in range(client_num):
        client_threads[i].join()
