# PyQt5 - GUI Library
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

# Standard Libraries
import socket
import threading
import time
import re

# ---------------------------- #

# Window Properties
WindowTitle = "Chat Room"
BackgroundColour = "black"
status = "Not Connected"
pattern = r"[a-zA-Z0-9()$%_/.]*$"

width = 680
height = 440

# Connection Properties
ServerIP = "0.0.0.0"
PORT = 10000
buffer = 1024

username = None
objSocket = None

class ChatWindow(QDialog):

    def __init__(self):
        super(ChatWindow, self).__init__()

        # Disable Maximize Button and Stretch
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
        self.setFixedSize(width, height)

        # Display Window Title
        self.setWindowTitle(WindowTitle)
        self.setWindowIcon(QtGui.QIcon("images/Chat_Icon.png"))
        self.setStyleSheet(f"background: {BackgroundColour}")

        # Display Server Status
        self.StatusLabel = QLabel("Status: ", self); self.StatusLabel.move(5, 10)
        self.StatusLabel.setObjectName("StatusLabel")

        self.ServerStatus = QLabel(f"{status}", self); self.ServerStatus.move(70, 10)
        self.ServerStatus.setObjectName("ServerStatusLabel")

        # Username Label & Display Username Box
        self.UsernameLabel = QLabel("Username: ", self);  self.UsernameLabel.move(5, 40)
        self.UsernameLabel.setObjectName("UsernameLabel")

        self.UsernameInput = QLineEdit(self); self.UsernameInput.setMaxLength(13); self.UsernameInput.move(105, 42)
        self.UsernameInput.setObjectName("UsernameInput")

        # Server IP Label & Display Server IP Box
        self.ServerIPLabel = QLabel("Server IP: ", self); self.ServerIPLabel.move(5, 70)
        self.ServerIPLabel.setObjectName("ServerIPLabel")

        self.ServerIPInput = QLineEdit(self); self.ServerIPInput.setMaxLength(15); self.ServerIPInput.move(105, 70)
        self.ServerIPInput.setObjectName("ServerIPInput")

        # Divider Line
        self.DividerLine = QLabel("_"*34, self); self.DividerLine.move(7, 100); self.DividerLine.setStyleSheet("color: white")

        # Connect to Server - Button
        self.ConnectButton = QPushButton("Connect", self); self.ConnectButton.setStyleSheet("background: grey")
        self.ConnectButton.move(10, 120); self.ConnectButton.setObjectName("ConnectButton")
        self.ConnectButton.clicked.connect(self.ServerConnect)

        # Disconnect from Server - Button
        self.DisconnectButton = QPushButton("Disconnect", self); self.DisconnectButton.setStyleSheet("background: grey")
        self.DisconnectButton.move(90, 120); self.DisconnectButton.setObjectName("DisconnectButton")
        self.DisconnectButton.clicked.connect(self.ServerDisconnect)

        # Clear Chat - Button
        self.ClearButton = QPushButton("Clear Chat", self); self.ClearButton.setStyleSheet("background: grey")
        self.ClearButton.move(565, 10); self.ClearButton.setObjectName("ClearButton")
        self.ClearButton.clicked.connect(self.ClearChat)

        # Chat Box to View Messages
        self.ChatBox = QTextEdit(self); self.ChatBox.move(220, 10); self.ChatBox.resize(340, 340)
        self.ChatBox.setStyleSheet("background: lightgrey"); self.ChatBox.setReadOnly(True)

        # Text Box (messages)
        self.InputBox = QTextEdit(self); self.InputBox.move(220, 355); self.InputBox.resize(340, 75)
        self.InputBox.setStyleSheet("background: white")

        # Send Message Button
        self.SendMessage = QPushButton("Send", self); self.SendMessage.move(565, 355); self.SendMessage.resize(110, 75)
        self.SendMessage.setStyleSheet("background: rgb(45, 45, 236)"); self.SendMessage.setObjectName("SendMessageButton")
        self.SendMessage.clicked.connect(self.Send)

        # Show Application
        self.show()

    # Username Character(s) error
    def ErrorMessageBox(self, ErrorMessage):
        MessageBox = QMessageBox(self)
        MessageBox.setIcon(QMessageBox.Critical)
        MessageBox.setWindowTitle("Error")
        MessageBox.setText(f"{ErrorMessage}\t")
        MessageBox.setStyleSheet("color: yellow")
        MessageBox.show()

    # Send Message
    def Send(self):
        InputText = self.InputBox.toPlainText()
        if (InputText.strip() == ""):
            return

        elif (len(InputText) >= 200):
            self.ChatBox.append("[-] Maximum of 200 Characters is only Permitted")
            self.InputBox.setText(None)
            return

        try:
            objSocket.send(bytes(InputText, "utf-8"))
        except:
            self.ChatBox.setText("<Not Connected to Server>")
        finally:
            self.InputBox.setText(None)

    # Disconnect from Server
    def ServerDisconnect(self):
        if (objSocket):
            objSocket.close()

            self.ChatBox.append("<Disconnected from Server>")
            self.Disconnected()
        else:
            self.ChatBox.setText("<Not Connected to Server>")

    # Connect to Server
    def ServerConnect(self):
        if (self.UsernameInput.text().strip() == ""):
            self.ErrorMessageBox("Invalid Username")
            return

        elif not (re.match(pattern, self.UsernameInput.text())):
            self.ErrorMessageBox("Invalid Username")
            return
        else:
            global username, ServerIP
            username = self.UsernameInput.text()
            ServerIP = self.ServerIPInput.text()

        self.ServerStatus.setText("Connecting...")
        self.ChatBox.setText(None)

        client = ClientThread(window)
        client.daemon = True
        client.start()

        self.UsernameInput.setReadOnly(True); self.ServerIPInput.setReadOnly(True)
        self.ConnectButton.setEnabled(False)

    # Clear Chat Log
    def ClearChat(self):
        self.ChatBox.setText(None)

    # Receive Data and Display Messages
    def ReceivedMessage(self, data):
        if (re.findall(username, data)):
            data = "You: " + data.split(':')[1]
            colour = "blue"

        elif (re.findall("disconnected", data)): colour = "red"
        elif (re.findall("connected", data)): colour = "green"
        else: colour = "black"

        self.ChatBox.append(f"<span style=color:{colour}>{data}</span>")

    # Display when connected to the server
    def Connected(self):
        self.ServerStatus.setText("Connected"); self.ServerStatus.setStyleSheet("color: green")

    # Display when disconnected from the server
    def Disconnected(self):
        self.ServerStatus.setText(f"{status}")
        self.ServerStatus.setStyleSheet("color: red")

        self.UsernameInput.setReadOnly(False)
        self.ServerIPInput.setReadOnly(False)
        self.ConnectButton.setEnabled(True)

    def AppendUsers(self, users):
        if (username in str(users)):
            users.remove(username)

        
        self.ConnectedUsersTable.append("\n".join(users))

class ClientThread(threading.Thread):

    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window = window

    def run(self):
        global objSocket
        objSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        time.sleep(0.1)
        while (True):
            try:
                objSocket.connect((ServerIP, PORT))
                objSocket.send(bytes(f"{username}", "utf-8"))
                self.window.Connected()
            except:
                continue
            else:
                break

        while (True):
            try:
                data = str(objSocket.recv(buffer), "utf-8")
                if not data:
                    raise Exception

                self.window.ReceivedMessage(data.split("|")[0])
            except:
                self.window.Disconnected()
                objSocket.close(); objSocket = None
                break

if __name__ == "__main__":
    application = QApplication([])
    with open("GUI-Styles.css", "r") as StyleFile:
        application.setStyleSheet(StyleFile.read())

    window = ChatWindow()
    exit(application.exec_())