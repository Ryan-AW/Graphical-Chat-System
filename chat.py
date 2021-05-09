# Standard Libraries
import socket
import threading
import re

# Encryption Library
from cryptography.fernet import Fernet

# PyQt5 - GUI Library
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

# GUI Properties
TITLE = "Chat Room"
BACKGROUND = "black"
WIDTH = 680
HEIGHT = 440

# Connection Properties
server = "0.0.0.0"
connStatus = "Not Connected"
PORT = 5005
BUFFER = 1024
KEY = None

username = None
objSocket = None

class ChatWindow(QDialog):

    def __init__(self):
        super(ChatWindow, self).__init__()

        # Disable Maximize Button & Stretch
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
        self.setFixedSize(WIDTH, HEIGHT)

        # Title | Icon | Background
        self.setWindowTitle(TITLE)
        self.setWindowIcon(QtGui.QIcon("images/icon.png"))
        self.setStyleSheet("background: {}".format(BACKGROUND))

        # Server Status
        self.StatusLabel = QLabel("Status: ", self); self.StatusLabel.move(5, 10)
        self.StatusLabel.setObjectName("StatusLabel")

        self.ServerStatusLabel = QLabel(f"{connStatus}", self); self.ServerStatusLabel.move(70, 10)
        self.ServerStatusLabel.setObjectName("ServerStatusLabel")

        # Username Box
        self.UsernameLabel = QLabel("Username: ", self);  self.UsernameLabel.move(5, 40)
        self.UsernameLabel.setObjectName("UsernameLabel")

        self.UsernameBox = QLineEdit(self); self.UsernameBox.setMaxLength(13); self.UsernameBox.move(105, 42)
        self.UsernameBox.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[a-zA-Z0-9]+")))
        self.UsernameBox.setObjectName("UsernameBox")

        # Server Box
        self.ServerLabel = QLabel("Server IP: ", self); self.ServerLabel.move(5, 70)
        self.ServerLabel.setObjectName("ServerLabel")

        self.ServerBox = QLineEdit(self); self.ServerBox.setMaxLength(15); self.ServerBox.move(105, 70)
        self.ServerBox.setObjectName("ServerBox")

        # Divider Line
        self.DividerLine = QLabel("_"*34, self); self.DividerLine.move(7, 100); self.DividerLine.setStyleSheet("color: white")

        # Chat Box (mode: readonly)
        self.ChatBox = QTextEdit(self); self.ChatBox.move(220, 10); self.ChatBox.resize(340, 340)
        self.ChatBox.setStyleSheet("background: lightgrey"); self.ChatBox.setReadOnly(True); self.ChatBox.setObjectName("ChatBox")

        # Text Box
        self.TextBox = QTextEdit(self); self.TextBox.move(220, 355); self.TextBox.resize(340, 75)
        self.TextBox.setStyleSheet("background: white")

        # Send Button
        self.SendMessage = QPushButton("Send", self); self.SendMessage.move(565, 355); self.SendMessage.resize(110, 75)
        self.SendMessage.setStyleSheet("background: rgb(45, 45, 236)"); self.SendMessage.setObjectName("SendButton")
        self.SendMessage.clicked.connect(self.Send)

        # Connect Button
        self.ConnectButton = QPushButton("Connect", self); self.ConnectButton.setStyleSheet("background: grey")
        self.ConnectButton.move(10, 120); self.ConnectButton.setObjectName("ConnectButton")
        self.ConnectButton.clicked.connect(self.ServerConnect)

        # Disconnect Button
        self.DisconnectButton = QPushButton("Disconnect", self); self.DisconnectButton.setStyleSheet("background: grey")
        self.DisconnectButton.move(90, 120); self.DisconnectButton.setObjectName("DisconnectButton")
        self.DisconnectButton.clicked.connect(self.ServerDisconnect)

        # Encryption Label
        self.EncryptionLabel = QLabel("🔴 Encryption: Secured", self)
        self.EncryptionLabel.setObjectName("EncryptionLabel"); self.EncryptionLabel.move(7, 150)

        # Clear Button
        self.ClearButton = QPushButton("Clear Chat", self); self.ClearButton.setStyleSheet("background: grey")
        self.ClearButton.move(565, 10); self.ClearButton.setObjectName("ClearButton")
        self.ClearButton.clicked.connect(lambda:self.ChatBox.setText(None))

        self.show()

    def ServerConnect(self):
        global username, server
        username = self.UsernameBox.text()
        server = self.ServerBox.text()

        if (len(self.UsernameBox.text().strip()) == 0 or len(self.ServerBox.text().strip()) == 0):
            self.ChatBox.append("You must provide a Username/Server IP")
            return

        self.ServerStatusLabel.setText("Connecting...")
        self.ChatBox.setText(None)

        client = ClientThread(window)
        client.daemon = True
        client.start()

        self.UsernameBox.setReadOnly(True); self.ServerBox.setReadOnly(True)
        self.ConnectButton.setEnabled(False)

    def ServerDisconnect(self):
        if (objSocket):
            objSocket.close()

            self.ChatBox.append("You have been disconnected")
            self.Disconnected()
        else:
            self.ChatBox.setText("You are not connected to a Server")

    def Send(self):
        text = self.TextBox.toPlainText()
        if (len(text) >= 200):
            self.ChatBox.append("[-] Maximum of 200 Characters Only")
            self.TextBox.setText(None)
            return

        elif (len(text.strip())== 0):
            return

        try:
            objSocket.send(Fernet(KEY).encrypt(bytes(text, "utf-8")))
        except:
            self.ChatBox.setText("You are not connected to a Server")
        finally:
            self.TextBox.setText(None)

    def ReceivedMessage(self, data):
        if (re.findall(username, data)):
            data = "You: " + data.split(':')[1]
            colour = "blue"

        elif (re.findall("disconnected", data)): colour = "red"
        elif (re.findall("connected", data)): colour = "green"
        else: colour = "black"

        self.ChatBox.append(f"<span style=color:{colour}>{data}</span>")

    def Disconnected(self):
        self.ServerStatusLabel.setText(connStatus)
        self.ServerStatusLabel.setStyleSheet("color: red")

        self.UsernameBox.setReadOnly(False)
        self.ServerBox.setReadOnly(False)
        self.ConnectButton.setEnabled(True)


class ClientThread(threading.Thread):

    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window = window

    def run(self):
        global objSocket, KEY
        objSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while (True):
            try:
                objSocket.connect((server, PORT))
            except:
                continue
            else:
                break

        KEY = objSocket.recv(1024)
        objSocket.send(Fernet(KEY).encrypt(bytes(username, "utf-8")))

        if (Fernet(KEY).decrypt(objSocket.recv(BUFFER)) == b"invalid"):
            self.window.ChatBox.append("Username has already been taken")
            self.window.Disconnected()
            exit(1)

        self.window.ServerStatusLabel.setText("Connected")
        self.window.ServerStatusLabel.setStyleSheet("color: green")

        while (True):
            try:
                data = Fernet(KEY).decrypt(objSocket.recv(BUFFER))
                if not data:
                    raise socket.error

                self.window.ReceivedMessage(str(data, "utf-8"))
            except:
                self.window.Disconnected()
                objSocket.close(); objSocket = None
                break

if __name__ == "__main__":
    application = QApplication([])
    application.setStyleSheet("""
    #StatusLabel, #UsernameLabel, #ServerLabel {
        color: grey;
        font-size: 19px;
    }
    #ServerStatusLabel {
        color: red;
        font-size: 19px;
    }
    #UsernameBox, #ServerBox {
        color: green;
        font-weight: bold;
        height: 20%;
        width: 80%;
    }
    #ConnectButton, #DisconnectButton, #ClearButton {
        color: blue;
        height: 15%;
        width: 60%;
    }
    #EncryptionLabel {
        color: green;
        font-weight: bold;
    }
    #SendButton {
        color: white;
        font-size: 15px;
    }
    #ChatBox { font-weight: bold; }
    """)
    window = ChatWindow()
    exit(application.exec_())
