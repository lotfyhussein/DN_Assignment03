# DN_Assignment03
    TODO:
        Fixed:-Download: Should it require the LIST_FILES command first
        Fine, but check:-UPLOAD the same file: Should it overwrite.
        CheckIfWorks:-In order to generate different MD5 hashes, file content must be diffrent
        -Killed client
            Traceback (most recent call last):
            File "server.py", line 103, in <module>
                data = connectSocket.recv(BUFFER_SIZE).decode()
            ConnectionResetError: [Errno 104] Connection reset by peer!!!!
        -Killed server during the running
        Fixed:-Handle the fact that no server is running
        Fixed:-Error LIST_FILES
            Enter command: LIST_FILES
            Traceback (most recent call last):
            File "client.py", line 116, in <module>
                received_file_list = handle_list_files(clientSocket)
            File "client.py", line 26, in handle_list_files
                size = int(msg)
            ValueError: invalid literal for int() with base 10: '5b19f0e9c93fabae107d6caff3af232c'