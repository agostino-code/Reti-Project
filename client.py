import os
import time
from socket import *

server_name = 'localhost'
server_port = 34561
current_path = os.getcwd()


def hostname():
    print('Hostname requested')
    host = gethostname()
    clientSocket.send(host.encode())


def user_logged():
    print('Username requested')
    username = os.getlogin()
    clientSocket.send(username.encode())


def ls():
    print('List directory requested')
    list_dir = os.walk(current_path)
    for root, dirs, files in list_dir:
        for dir in dirs:
            clientSocket.send(dir.encode())
            time.sleep(0.1)

        clientSocket.send('/'.encode())

        for file in files:
            clientSocket.send(file.encode())
            time.sleep(0.1)

        clientSocket.send('.'.encode())
        break


def cd():
    global current_path
    print('Change directory requested')
    path = clientSocket.recv(1024).decode()
    try:
        os.chdir(path)
        current_path = path
        clientSocket.send(current_path.encode())
    except FileNotFoundError:
        print('Path not found')
        clientSocket.send('Path not found'.encode())


def pwd():
    print('Working directory requested')
    clientSocket.send(os.getcwdb())


switcher = {
    'hostname': hostname,
    'user': user_logged,
    'ls': ls,
    'cd': cd,
    'pwd': pwd}

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
        except ConnectionError:
            print('Server disconnected')
            # wait 5 seconds
            clientSocket.shutdown(SHUT_RDWR)
            clientSocket.close()
            connected = False
            time.sleep(10)
            os.system('cls')
