from socket import *
import hashlib
import os
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


def handle_list_files(clientSocket):
    msg = clientSocket.recv(BUFFER_SIZE).decode()
    if msg == "No files available at the moment":
        print("Server Response: No files available at the moment")
        return None
    rsize = 0
    size = int(msg)
    clientSocket.send("start".encode())
    data = ''
    while True:
        data += clientSocket.recv(BUFFER_SIZE).decode()
        rsize += len(data)
        if (rsize >= size):
            print(data)
            return data.splitlines()

def handle_upload(clientSocket):
    clientSocket.recv(BUFFER_SIZE).decode()
    filename = input('Enter filename to be sent: ')
    file_size = getFileSize(path + '/' + filename)
    msg = filename + ';' + str(file_size)
    clientSocket.send(msg.encode())
    clientSocket.recv(BUFFER_SIZE).decode() # wait for server's "Ready to receive a file" msg
    ###
    # start sending the file
    ###
    f = open(path + '/' + filename, "rb")
    data = f.read(1024)
    while (data):
       clientSocket.send(data)
       data = f.read(1024)
    f.close()
    print('Sent ({} bytes)'.format(file_size)) 

    ###
    # MD5 Veirifcation Porcess
    ###
    md5_server = clientSocket.recv(BUFFER_SIZE).decode() # get Md5 hash from server
    f = open(path + '/' + filename, "rb")
    file_data = f.read()
    md5_local = generate_md5_hash(file_data)
    if md5_server != md5_local:
        print("Fail")
    else:
        print("Success!")
    return

def handle_download(clientSocket, received_file_list):
    clientSocket.recv(BUFFER_SIZE).decode()
    file_id = input('Enter file id: ')
    for f in received_file_list:
        l = f.split(';')
        if l[0] == file_id:
            filename = l[0] + l[1]
            size = int(l[2])
    if not size:
        print('No such file available!')
        return
    clientSocket.send(file_id.encode())
    rsize = 0
    with open(path + '/' + filename , 'wb') as f:
        while True:
            data =  clientSocket.recv(BUFFER_SIZE)
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


# Create TCP socket for future connections
#
clientSocket = socket(AF_INET, SOCK_STREAM)
# 
# Connect the client to the specified server
#
clientSocket.connect((serverURL, serverPort))
print("Client connected to server: " + serverURL + ":" + str(serverPort))

received_file_list = []
while True:
    command = input('Enter command: ')
    if command == "LIST_FILES":
        clientSocket.send(command.encode())
        received_file_list = handle_list_files(clientSocket)
    elif command == "UPLOAD":
        clientSocket.send(command.encode())
        handle_upload(clientSocket)
    elif command == "DOWNLOAD":
        # Empty received list
        if not received_file_list:
            print("List all the files first!")
        else:
            clientSocket.send(command.encode())
            handle_download(clientSocket, received_file_list)
    elif command == "DISCONNECT":
        clientSocket.send(command.encode())
        clientSocket.close()
        break
    else:
        print('Unknown Command')
