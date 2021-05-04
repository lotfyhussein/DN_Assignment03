from socket import *
import hashlib
import os
import sys

serverPort = 7700
serverURL = "localhost"
BUFFER_SIZE = 1024
path = './Client_Files'


def generate_md5_hash (file_data):
    md5_hash = hashlib.md5(file_data)
    f_id = md5_hash.hexdigest()
    return str(f_id)

def getFileSize(filename):
    st = os.stat(filename)
    return st.st_size

# Error handling send and receive
def recv_safe(clientSocket, BUFFER_SIZE):
    try:
        return clientSocket.recv(BUFFER_SIZE)
    except:
        print("Receive Error::TODO fix")

def send_safe(clientSocket, data):
    try:
        clientSocket.send(data)
    except:
        print("Send Error::TODO fix")

def handle_list_files(clientSocket):
    msg = recv_safe(clientSocket, BUFFER_SIZE).decode()
    if msg == "No files available at the moment":
        print("Server Response: No files available at the moment")
        return None
    rsize = 0
    size = int(msg)
    send_safe(clientSocket, "start".encode())
    full_msg = ''
    while True:
        data = recv_safe(clientSocket, BUFFER_SIZE).decode()
        rsize += len(data)
        full_msg += data
        if (rsize >= size):
            print(full_msg)
            return full_msg.splitlines()

def handle_upload(clientSocket):
    recv_safe(clientSocket, BUFFER_SIZE).decode()
    filename = input('Enter filename to be sent: ')
    file_size = getFileSize(path + '/' + filename)
    msg = filename + ';' + str(file_size)
    send_safe(clientSocket, msg.encode())
    recv_safe(clientSocket, BUFFER_SIZE).decode() # wait for server's "Ready to receive a file" msg
    ###
    # start sending the file
    ###
    f = open(path + '/' + filename, "rb")
    data = f.read(1024)
    while (data):
       send_safe(clientSocket, data)
       data = f.read(1024)
    f.close()
    print('Sent ({} bytes)'.format(file_size)) 

    ###
    # MD5 Veirifcation Porcess
    ###
    md5_server = recv_safe(clientSocket, BUFFER_SIZE).decode() # get Md5 hash from server
    f = open(path + '/' + filename, "rb")
    file_data = f.read()
    md5_local = generate_md5_hash(file_data)
    if md5_server != md5_local:
        print("Fail")
    else:
        print("Success!")
    return

def handle_download(clientSocket, received_file_list):
    recv_safe(clientSocket, BUFFER_SIZE).decode()
    file_id = input('Enter file id: ')
    for f in received_file_list:
        l = f.split(';')
        if l[0] == file_id:
            filename = l[0] + l[1]
            size = int(l[2])
    if not size:
        print('No such file available!')
        return
    send_safe(clientSocket, file_id.encode())
    rsize = 0
    with open(path + '/' + filename , 'wb') as f:
        while True:
            data =  recv_safe(clientSocket, BUFFER_SIZE)
            rsize += len(data)
            f.write(data)
            if (rsize >= size):
                break
    f.close()
    print('Recieved ({} bytes)'.format(size)) 
    ###
    # Generate MD5 Hash and compare it to file_id
    ###
    f = open(path + '/' + filename, "rb")
    file_data = f.read()
    md5_hash = generate_md5_hash(file_data)
    if md5_hash != file_id:
        print("Fail")
    else:
        print("Success!")
    return

# Create TCP socket for connections with the server
clientSocket = socket(AF_INET, SOCK_STREAM)

# Try to connect the client to the specified server
try:
    clientSocket.connect((serverURL, serverPort))
except:
    sys.exit("Server is not running. Please try to connect later!")

print("Client connected to server: " + serverURL + ":" + str(serverPort))

received_file_list = []
while True:
    command = input('Enter command: ')
    if command == "LIST_FILES":
        send_safe(clientSocket, command.encode())
        received_file_list = handle_list_files(clientSocket)
    elif command == "UPLOAD":
        send_safe(clientSocket, command.encode())
        handle_upload(clientSocket)
    elif command == "DOWNLOAD":
        # Handle empty received list
        if not received_file_list:
            print("List all the files first!")
        else:
            send_safe(clientSocket, command.encode())
            handle_download(clientSocket, received_file_list)
    elif command == "DISCONNECT":
        send_safe(clientSocket, command.encode())
        clientSocket.close()
        break
    else:
        print('Unknown Command')