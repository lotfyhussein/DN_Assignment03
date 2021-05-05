# Assignment03
 
Fully functioning third assignment for the course _Data Networks_. Program was tested on both Windows and Linux. Assignment was tested on same machine (local host) and mulitple machines on same local network. You can also get the latest version of the assignment on GitHub: https://github.com/lotfyhussein/DN_Assignment03.git.
 
### Running the code
To start the server
```
python3 server.py [Server_IPv4_Address]
```
To start the client
```
python3 client.py [Server_IPv4_Address]
```
 
### Additional features 
- __DISCONNECT__ command to enable the client to disconnect from the server at any time.
- Handling sudden connection drop of either the client or the server.
- Client can handle large file list received from server.
- __UPLOAD__ command with automatic file size extraction.
- Sending/Receiving large files (tested with video files of ~1GB).
- Handling invalid user input such as wrong command, wrong filename or file_id.
 
### Notes:
- _Client_Files_ and _Server_Files_ directories were created to separate client files from server files when the program is excuted on the same machine. Please make sure to have _Server_Files_ directory, as we do not provide any files in it.
- Since there is no deletion operation defined in the task, it's assumed that the file list received from server exists when __DOWNLOAD__ command is sent to the server.