import os
import time
from socket import *


def print_and_log(text):
    print(text)
    with open(outputfilename, 'a') as outputfile:
        outputfile.write(text + '\n')


def log(text):
    with open(outputfilename, 'a') as outputfile:
        outputfile.write(text + ': ')


server_port = 50000
serverSoket = socket(AF_INET, SOCK_STREAM)
serverSoket.bind(('', server_port))
serverSoket.listen(1)


def command_sender():
    global outputfilename
    global connectionSocket
    connected = False
    while True:
        while not connected:
            try:
                print('Server listening on port', server_port)
                print('Waiting for a new connection')
                connectionSocket, addr = serverSoket.accept()
                outputfilename = str(addr) + ".log"
                print_and_log('New connection from ' + str(addr))
                connected = True
            except ConnectionRefusedError:
                print('Server not available')
                connected = False
                # wait 5 seconds
                time.sleep(10)

        while connected:
            try:
                command = input('>> ')
                if command in switcher.keys() and command != '':
                    switcher[command]()
                else:
                    print('Command not recognized')
                    # raise ValueError("Command not recognized")
            except ConnectionResetError:
                print_and_log('A client has disconnected')
                print()
                input('Press enter to continue')
                os.system('cls')
                connected = False


def hostname():
    connectionSocket.send('hostname'.encode())
    host = connectionSocket.recv(1024).decode()
    log('Hostname requested')
    print_and_log(host)


def user_logged():
    connectionSocket.send('user'.encode())
    ret = connectionSocket.recv(1024).decode()
    log('Username requested')
    print_and_log(ret)


def close_program():
    serverSoket.close()
    log('A client has disconnected')
    print_and_log('Server closed')
    quit()


switcher = {
    'hostname': hostname,
    'user': user_logged,
    'exit': close_program
}

if __name__ == '__main__':
    command_sender()
