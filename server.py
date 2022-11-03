import os
import sys
from socket import *

server_port = 34561
serverSoket = socket(AF_INET, SOCK_STREAM)
serverSoket.bind(('', server_port))
serverSoket.listen(1)
STOCK = '\033[0;0m'
BLUE = '\033[1;34m'


def hostname():
    connectionSocket.send('hostname'.encode())
    host = connectionSocket.recv(1024).decode()
    print(host)


def user_logged():
    connectionSocket.send('user'.encode())
    ret = connectionSocket.recv(1024).decode()
    print(ret)


def close_program():
    serverSoket.close()
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
            print('\t'+ret)


# def cd():
#     global current_path
#     connectionSocket.send('cd'.encode())
#     path = input('cd : Enter path to navigate >> ')
#     connectionSocket.send(path.encode())
#     ret = connectionSocket.recv(1024).decode()
#     if ret == 'Path not found':
#         print('Path not found')
#     else:
#         current_path = ret


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


def cdroot():
    global current_path
    connectionSocket.send('cdroot'.encode())
    ret = connectionSocket.recv(1024).decode()
    current_path = ret


def join():
    global current_path
    connectionSocket.send('join'.encode())
    filename = input('join : Enter directory name to join >> ')
    connectionSocket.send(filename.encode())
    ret = connectionSocket.recv(1024).decode()
    if ret == 'Directory not found':
        print('Directory not found')
    else:
        print('Directory joined')
        current_path = ret


def pwd():
    connectionSocket.send('pwd'.encode())
    ret = connectionSocket.recv(1024).decode()
    return ret


def get():
    connectionSocket.send('get'.encode())
    filename = input('get : Enter file name to download >> ')
    connectionSocket.send(filename.encode())
    ret = connectionSocket.recv(1024).decode()
    if ret == 'File not found':
        print('File not found')
    else:
        with open(filename, 'wb') as file:
            file.write(ret.encode())
            print('File downloaded')


def getall():
    connectionSocket.send('getall'.encode())
    filename = input('getall : Enter Output file name >> ')
    ret = connectionSocket.recv(1024)
    if ret == 'File not found':
        print('File not found')
    else:
        with open(filename + '.zip', 'wb') as file:
            file.write(ret)
            print('File downloaded')


switcher = {
    'hostname': hostname,
    'user': user_logged,
    'exit': close_program,
    'ls': ls,
    'get': get,
    'getall': getall,
    'cdup': cdup,
    'cdhome': cdhome,
    'cdroot': cdroot,
    'join': join}

connected = False
while True:
    while not connected:
        print('Server listening on port', server_port)
        print('Waiting for a new connection')
        connectionSocket, addr = serverSoket.accept()
        outputfilename = str(addr) + ".log"
        current_path = pwd()
        print('New connection from ' + str(addr))
        connected = True

    while connected:
        try:
            command = input(current_path + ' >> ')
            try:
                connectionSocket.send(''.encode())
            except ConnectionError:
                connected = False
            if command in switcher.keys() and command != '':
                switcher[command]()
            else:
                print('Command not recognized')
                # raise ValueError("Command not recognized")
        except ConnectionError:
            sys.stdout.write(STOCK)
            print('A client has disconnected')
            print()
            input('Press enter to continue')
            os.system('cls')
            connected = False
