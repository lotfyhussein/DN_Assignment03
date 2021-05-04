from socket import *
import hashlib
import os

path = './Server_Files'
serverPort = 7700
serverURL = "localhost"
BUFFER_SIZE = 1024

def generate_md5_hash (file_data):
    md5_hash = hashlib.md5(file_data)
    f_id = md5_hash.hexdigest()
    return str(f_id)

def getFileList(files):
    size = 0
    msg_list = []
    for f in files:
        file_size = getFileSize(path + '/' + f)
        msg = f + ';' + str(file_size)
        size += len(msg)
        msg_list.append(msg)
    return msg_list, size

def getFileSize(filename):
    st = os.stat(filename)
    return st.st_size

def handle_list_files(connectSocket):
    files = os.listdir(path)
    if len(files) == 0:
        connectSocket.send(str("No files available at the moment").encode())
    else:            
        msg_list, msg_size = getFileList(files)
        connectSocket.send(str(msg_size).encode())
        conf = connectSocket.recv(BUFFER_SIZE).decode()
        for f in msg_list:
            connectSocket.send((f + '\n').encode())
    return

def handle_upload(connectSocket):
    connectSocket.send("Please send file name and file size".encode())
    msg = connectSocket.recv(BUFFER_SIZE).decode()
    msg_split = msg.split(";")
    filename = msg_split[0]
    size = int(msg_split[1])
    rsize = 0
    connectSocket.send("Ready to receive a file".encode())
    with open(path + '/' + filename, 'wb') as f:
        while True:
            data = connectSocket.recv(BUFFER_SIZE)
            rsize += len(data)
            f.write(data)
            if (rsize >= size):
                break
    f.close()
    ###
    # Generate MD5 Hash and send it to the client
    ###
    f = open(path + '/' + filename, "rb")
    file_data = f.read()
    md5_hash = generate_md5_hash(file_data)
    connectSocket.send(md5_hash.encode())
    os.rename(path + '/' + filename, path + '/' + md5_hash + ';' + filename)
    print('Successfully received the file ({} bytes)'.format(size)) 
    return 

def handle_download(connectSocket):
    connectSocket.send("Please send a file ID".encode())
    file_id = connectSocket.recv(BUFFER_SIZE).decode()
    files = os.listdir(path)
    file_list, _ = getFileList(files)
    for f in file_list:
        l = f.split(';')
        if l[0] == file_id:
            filename = l[0] + ';' + l[1]
            size = int(l[2])
    ###
    # start sending the file
    ###
    f = open(path + '/' + filename, "rb")
    data = f.read(1024)
    while (data):
       connectSocket.send(data)
       data = f.read(1024)
    f.close()
    print('Successfully sent the file ({} bytes)'.format(size)) 
    return



serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((serverURL, serverPort))
serverSocket.listen(1)
print("Server is listening on port: " + str(serverPort))

while True:
    # 
    # Accept incoming client connection
    #
    connectSocket, addr = serverSocket.accept()
    print("Client connected: " + str(addr))
    while True:
        data = connectSocket.recv(BUFFER_SIZE).decode()
        if not data:
            continue
        if data == "LIST_FILES":
            handle_list_files(connectSocket)
        elif data == "UPLOAD":
            handle_upload(connectSocket)
        elif data == "DOWNLOAD":
            handle_download(connectSocket)
        elif data == "DISCONNECT":
            print("Client disconnected")
            connectSocket.close()
            break