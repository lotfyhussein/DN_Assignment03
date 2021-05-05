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
    try:
        files = os.listdir(path)
        if len(files) == 0:
            connectSocket.send(str("No files available at the moment").encode())
        else:            
            msg_list, msg_size = getFileList(files)
            connectSocket.send(str(msg_size).encode())
            conf = connectSocket.recv(BUFFER_SIZE).decode()
            for f in msg_list:
                connectSocket.send((f + '\n').encode())
        return True

    except Exception as e:
        print(e)
        print("Connection with client dropped!")
        return False

def handle_upload(connectSocket):
    try:
        # Querying filename and size
        connectSocket.send("Please send file name and file size".encode())
        msg = connectSocket.recv(BUFFER_SIZE).decode()

        # If we received an ABORT message from client due to bad user input, return
        if msg == "ABORT":
            return True

        msg_split = msg.split(";")
        filename = msg_split[0]
        size = int(msg_split[1])
        
        # Receiving file data
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
        
        # Generate MD5 hash
        f = open(path + '/' + filename, "rb")
        file_data = f.read()
        md5_hash = generate_md5_hash(file_data)
        f.close()

        # Add MD5 hash to the file name.
        # For Windows file with the same name has to be removed
        try:
            for f in os.listdir(path):
                if f == (md5_hash + ';' + filename):
                    os.remove(path + '/' + md5_hash + ';' + filename)
            os.rename(path + '/' + filename, path + '/' + md5_hash + ';' + filename)
        except:
            print("Error managing the received file!")
            return False

        # Send MD5 has to the client as confirmation
        connectSocket.send(md5_hash.encode())

        print('Successfully received the file ({} bytes)'.format(size))
        return True

    except Exception as e:
        print(e)
        print("Connection dropped!")
        return False

def handle_download(connectSocket):
    try:
        connectSocket.send("Please send a file ID".encode())
        file_id = connectSocket.recv(BUFFER_SIZE).decode()

        # If we received an ABORT message from client due to bad user input, return
        if file_id == "ABORT":
            return True

        files = os.listdir(path)
        file_list, _ = getFileList(files)
        for f in file_list:
            l = f.split(';')
            if l[0] == file_id:
                filename = l[0] + ';' + l[1]
                size = int(l[2])
        
        # Start sending the file
        f = open(path + '/' + filename, "rb")
        data = f.read(1024)
        while (data):
            connectSocket.send(data)
            data = f.read(1024)
        f.close()
        print('Successfully sent the file ({} bytes)'.format(size)) 
        return True

    except Exception as e:
        print(e)
        print("Connection dropped!")
        return False


# Listen for the client connections
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((serverURL, serverPort))
serverSocket.listen(1)
print("Server is listening on port: " + str(serverPort))

while True:
    # Accept incoming client connection
    connectSocket, addr = serverSocket.accept()
    print("Client connected: " + str(addr))

    error_occured = False
    while True:
        try:
            data = connectSocket.recv(BUFFER_SIZE).decode()
            if not data:
                continue
            if data == "LIST_FILES":
                error_occured = not handle_list_files(connectSocket)
            elif data == "UPLOAD":
                error_occured = not handle_upload(connectSocket)
            elif data == "DOWNLOAD":
                error_occured = not handle_download(connectSocket)
            elif data == "DISCONNECT":
                print("Client disconnected")
                connectSocket.close()
                break

            # If error occured with the connection with the client
            # close the connect socket
            if error_occured:
                connectSocket.close()
                break
        except:
            print("Client disconnected forcefully")
            break