import os
import sys
import time
from socket import *


def print_and_log(text):
    print(text)
    with open(outputfilename, 'a') as outputfile:
        outputfile.write(text + '\n')


def log(text):
    with open(outputfilename, 'a') as outputfile:
        outputfile.write(text + '\n')


server_port = 34561
serverSoket = socket(AF_INET, SOCK_STREAM)
serverSoket.bind(('', server_port))
serverSoket.listen(1)
STOCK = '\033[0;0m'
BLUE = '\033[1;34m'


def hostname():
    connectionSocket.send('hostname'.encode())
    host = connectionSocket.recv(1024).decode()
    log('Hostname requested: ')
    print_and_log(host)
    log('\n')


def user_logged():
    connectionSocket.send('user'.encode())
    ret = connectionSocket.recv(1024).decode()
    log('Username requested: ')
    print_and_log(ret)
    log('\n')


def close_program():
    serverSoket.close()
    log('A client has disconnected...')
    print_and_log('Server closed')
    quit()


def ls():
    connectionSocket.send('ls'.encode())
    log('List directory for ' + current_path)
    sys.stdout.write(BLUE)
    while True:
        ret = connectionSocket.recv(1024).decode()
        if ret == '/':
            sys.stdout.write(STOCK)
        else:
            if ret == '.':
                break
            log('\t' + ret)
            print(ret)

    log('\n')


def cd():
    global current_path
    connectionSocket.send('cd'.encode())
    path = input('cd >> ')
    connectionSocket.send(path.encode())
    ret = connectionSocket.recv(1024).decode()
    if ret == 'Path not found':
        print('Path not found')
    else:
        log('Change directory requested: ' + path)
        current_path = ret


def pwd():
    connectionSocket.send('pwd'.encode())
    ret = connectionSocket.recv(1024).decode()
    return ret


switcher = {
    'hostname': hostname,
    'user': user_logged,
    'exit': close_program,
    'ls': ls,
    'cd': cd
}

connected = False
while True:
    while not connected:
            print('Server listening on port', server_port)
            print('Waiting for a new connection')
            connectionSocket, addr = serverSoket.accept()
            outputfilename = str(addr) + ".log"
            current_path = pwd()
            print_and_log('New connection from ' + str(addr))
            log('\n')
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
            print_and_log('A client has disconnected')
            print()
            input('Press enter to continue')
            os.system('cls')
            connected = False
