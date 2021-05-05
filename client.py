from socket import *
import hashlib
import os
import sys

serverPort = 7700
serverURL = "localhost"
BUFFER_SIZE = 1024
path = './Client_Files'
received_file_list = []

def generate_md5_hash (file_data):
    md5_hash = hashlib.md5(file_data)
    f_id = md5_hash.hexdigest()
    return str(f_id)

def getFileSize(filename):
    st = os.stat(filename)
    return st.st_size


def handle_list_files(clientSocket, command):
    try:
        # Processing the commnad
        clientSocket.send(command.encode())

        # Receive the size of the list in bytes
        msg = clientSocket.recv(BUFFER_SIZE).decode()

        # Handle empty list
        if msg == "No files available at the moment":
            print("Server Response: No files available at the moment")
            return True
        # Get the msg size
        size = int(msg)
        # Tell the server to start sending the msg
        clientSocket.send("start".encode())

        # Start receiving the msg
        full_msg = ''
        rsize = 0
        while True:
            data = clientSocket.recv(BUFFER_SIZE).decode()
            rsize += len(data)
            full_msg += data
            if (rsize >= size):
                print(full_msg)
                # Update the global list
                global received_file_list
                received_file_list = full_msg.splitlines()
                return True
    except:
        return False

def handle_upload(clientSocket, command):
    try:
        # Processing the commnad
        clientSocket.send(command.encode())

        # Wait for server confimation
        msg = clientSocket.recv(BUFFER_SIZE).decode()

        # Get file name from user
        try:
            filename = input('Enter filename to be sent: ')
            file_size = getFileSize(path + '/' + filename)
        except:
            print("File Not Found!")
            clientSocket.send("ABORT".encode())
            return True

        # Prepare the filename and size and send it to the server
        msg = filename + ';' + str(file_size)
        clientSocket.send(msg.encode())
        # Wait for server's "Ready to receive a file" msg
        msg = clientSocket.recv(BUFFER_SIZE).decode()
        print("Server Response: " + msg)

        # Start sending the file
        print("Sending...")
        f = open(path + '/' + filename, "rb")
        data = f.read(1024)
        while (data):
            clientSocket.send(data)
            data = f.read(1024)
        f.close()
        print('Sent ({} bytes)'.format(file_size)) 

        # MD5 Veirifcation Porcess
        md5_server = clientSocket.recv(BUFFER_SIZE).decode() # get Md5 hash from server
        f = open(path + '/' + filename, "rb")
        file_data = f.read()
        md5_local = generate_md5_hash(file_data)
        if md5_server != md5_local:
            print("Fail")
        else:
            print("Success!")
        return True
    except:
        return False

def handle_download(clientSocket, command):
    try:
        # Processing the commnad
        clientSocket.send(command.encode())

        # Wait for server confirmation
        msg = clientSocket.recv(BUFFER_SIZE).decode()

        # Get file id from user
        file_id = input('Enter file id: ')
        filename = ''
        for f in received_file_list:
            l = f.split(';')
            if l[0] == file_id:
                filename = l[0] + l[1]
                size = int(l[2])
        if filename == '':
            print('No such file available!')
            clientSocket.send("ABORT".encode())
            return True

        # Send file id to the server
        clientSocket.send(file_id.encode())

        # Start recieving the file
        rsize = 0
        with open(path + '/' + filename , 'wb') as f:
            while True:
                data = clientSocket.recv(BUFFER_SIZE)
                rsize += len(data)
                f.write(data)
                if (rsize >= size):
                    break
        f.close()
        print('Recieved ({} bytes)'.format(size)) 


        # Generate MD5 Hash and compare it to file_id
        f = open(path + '/' + filename, "rb")
        file_data = f.read()
        md5_hash = generate_md5_hash(file_data)
        if md5_hash != file_id:
            print("Fail")
        else:
            print("Success!")
        return True
    except:
        return False

# Check if server is on local host or on 
# IPv4 address provided in input.
if len(sys.argv) == 2:
    try:
        serverURL = sys.argv[1]
    except Exception as e:
        print(e)

# Create TCP socket for connections with the server
clientSocket = socket(AF_INET, SOCK_STREAM)

# Try to connect the client to the specified server
try:
    clientSocket.connect((serverURL, serverPort))
except:
    sys.exit("Server is not running. Please try to connect later!")

print("Client connected to server: " + serverURL + ":" + str(serverPort))

connection_error = False
while True:
    command = input('Enter command: ')
    if command == "LIST_FILES":
        connection_error = not handle_list_files(clientSocket, command)
    elif command == "UPLOAD":
        connection_error = not handle_upload(clientSocket, command)
    elif command == "DOWNLOAD":
        # Handle empty received list
        if not received_file_list:
            print("List all the files first!")
        else:
            connection_error = not handle_download(clientSocket, command) 
    elif command == "DISCONNECT":
            clientSocket.send(command.encode())
            clientSocket.close()
            break
    else:
        print('Unknown Command')

    # Check if error happend in any of the commands
    if connection_error:
        print("Connection dropped")
        clientSocket.close()
        break