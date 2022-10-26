import os
import time
from socket import *

server_name = 'localhost'
server_port = 50000


def hostname():
    print('Hostname requested')
    host = gethostname()
    clientSocket.send(host.encode())


def user_logged():
    print('Username requested')
    username = os.getlogin()
    clientSocket.send(username.encode())


switcher = {
    'hostname': hostname,
    'user': user_logged}

connected = False
while True:

    while not connected:
        try:
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.connect((server_name, server_port))
            connected = True
            print("re-connection successful")

        except ConnectionRefusedError:
            print('Server not available')
            connected = False
            # wait 5 seconds
            time.sleep(10)

    while connected:
        try:
            command = clientSocket.recv(1024).decode()
            if command in switcher.keys() and command != '':
                print('Command received: ', command)
                switcher[command]()
        except ConnectionResetError:
            print('Server disconnected')
            # wait 5 seconds
            clientSocket.shutdown(SHUT_RDWR)
            clientSocket.close()
            connected = False
            time.sleep(10)
