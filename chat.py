# PyQt5 - GUI Libraries
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

# Standard Libraries
import socket
import threading
import os
import time
import re

# ---------------------------- #
WindowTitle = "LAN - Chat"
WindowColour = "#34495E"
status = "Not Connected"
pattern = r"[a-zA-Z0-9()$%_/.]*$"

width = 580
height = 340

# Socket Properties
ServerIP = ""
PORT = 10000
bufsize = 0x400

# Main Chat Window
class ChatWindow(QDialog):

    def __init__(self):
        super(ChatWindow, self).__init__()

        # Disable Maximize Button and Stretch
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
        self.setFixedSize(width, height)

        # Display Window Title
        self.setWindowTitle(WindowTitle)
        self.setWindowIcon(QtGui.QIcon("images/chat.png"))
        self.setStyleSheet(f"background: {WindowColour}")

        # Display Server Status
        self.StatusLabel = QLabel("Status: ", self); self.StatusLabel.move(10, 5); self.StatusLabel.setFont(QFont("Arial Bold", 13)); self.StatusLabel.setStyleSheet("color: red")
        self.ServerStatus = QLabel(f"({status})", self); self.ServerStatus.move(70, 2); self.ServerStatus.setFont(QFont("Arial Bold", 13)); self.ServerStatus.resize(165, 25)

        # Display Username
        self.UsernameLabel = QLabel("Username: ", self); self.UsernameLabel.move(10, 30); self.UsernameLabel.setFont(QFont("Arial Bold", 13)); self.UsernameLabel.setStyleSheet("color: red")
        self.UsernameInput = QLineEdit(self); self.UsernameInput.move(98, 30); self.UsernameInput.setStyleSheet("background: black; color: white"); self.UsernameInput.resize(105, 20)
        self.UsernameInput.setMaxLength(12)

        self.DividerLine = QLabel("_"*35, self); self.DividerLine.move(12, 50)

        # Connect to Server - Button
        self.Connect_Button = QPushButton("<Connect>", self); self.Connect_Button.move(10, 70); self.Connect_Button.setStyleSheet("background: grey; color: blue")
        self.Connect_Button.clicked.connect(self.ServerConnect)

        # Clear Chat - Button
        self.ClearChat_Button = QPushButton("Clear Chat", self); self.ClearChat_Button.move(10, 100); self.ClearChat_Button.setStyleSheet("background: grey; color: blue")
        self.ClearChat_Button.clicked.connect(self.ClearChat)

        # Chat Box to View Messages
        self.ChatBox = QTextEdit(self); self.ChatBox.move(270, 10); self.ChatBox.resize(290, 250); self.ChatBox.setStyleSheet("background: lightgrey")
        self.ChatBox.setReadOnly(True)

        # Text Box (messages)
        self.InputBox = QTextEdit(self); self.InputBox.move(270, 270); self.InputBox.resize(220, 50); self.InputBox.setStyleSheet("background: white")

        # Send Message Button
        self.SendMessage = QPushButton("<Send>", self); self.SendMessage.move(500, 270); self.SendMessage.resize(60, 25); self.SendMessage.setStyleSheet("background: grey; color: blue")
        self.SendMessage.clicked.connect(self.Send)

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

        elif (len(InputText) > 200):
            self.ChatBox.append("[-] Maximum of 200 Characters is only Permitted")
            self.InputBox.setText(None)
            return

        try:
            objSocket.send(bytes(InputText, "utf-8"))
        except:
            self.ChatBox.setText("<Not Connected to Server>")
        finally:
            self.InputBox.setText(None)

    # Connect to Server
    def ServerConnect(self):
        if (self.UsernameInput.text().strip() == ""):
            self.ErrorMessageBox("Invalid Username")
            return

        elif not (re.match(pattern, self.UsernameInput.text())):
            self.ErrorMessageBox("Invalid Username")
            return
        else:
            global username
            username = self.UsernameInput.text()

        self.ServerStatus.setText("Connecting...")
        self.ChatBox.setText(None)

        client = ClientThread(window)
        client.daemon = True
        client.start()

        self.UsernameInput.setReadOnly(True)
        self.Connect_Button.setText("<Disconnect>"); self.Connect_Button.clicked.connect(self.close)

    # Clear Chat Log
    def ClearChat(self):
        self.ChatBox.setText(None)

    # Receive and Display Messages
    def ReceivedMessage(self, data):
        self.ChatBox.append(data)

    # Indicate and Display when connected to server
    def Connected(self):
        self.ChatBox.append(f"[Connected to Server]\n" + "-"*70)
        self.ServerStatus.setText("(Connected)")

    # Indicate and Display when disconnected to server
    def Disconnected(self):
        self.ChatBox.append("<You have been Disconnected>")
        self.ServerStatus.setText(f"({status})")

        self.UsernameInput.setReadOnly(False)

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
                data = objSocket.recv(bufsize).decode()
                if not data:
                    raise Exception
                self.window.ReceivedMessage(data)

            except:
                self.window.Disconnected(); objSocket.close(); del(objSocket)
                break

if __name__ == "__main__":
    application = QApplication([])
    window = ChatWindow()
    exit(application.exec_())
