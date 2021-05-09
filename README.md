# Graphical-Chat-System
A Chat System with a Graphical User Interface written in Python 3 utilizing the PyQt5 Library and Fernet Encryption Library for sending and receiving messages safely.
This Chat System works on any Local Area Network and can be extended to work anywhere on different networks for clients to connect to but must be forwarded to Port: 5005 (as set)

<Server>
- (server.py) must be running to allow clients to connect and communicate
- ability to log all messages and display connected users
- no limit to how many clients can connect

<Client>
- (chat.py) must be binded to the Server IP Address
- ability to send and receive messages with end-to-end encryption


![](images/interface.png)
