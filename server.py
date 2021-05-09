# Standard Libraries
import socket
import threading
import os

# Encryption Library
from cryptography.fernet import Fernet

# Third Party Libraries
from prettytable import PrettyTable

# Connection Properties
SERVER = "0.0.0.0"
PORT = 5005
BUFFER = 1024
KEY = Fernet.generate_key()

conn = None
users = []

table = PrettyTable()
table.field_names = ["Username", "IP Address"]

os.system("clear" if os.name == "posix" else "cls")

class Server:
    objSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    objSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connections = []

    def __init__(self):
        self.objSocket.bind((SERVER, PORT))
        self.objSocket.listen(socket.SOMAXCONN)
        print("<Server Log Active>\n" + "-"*19)

    def handler(self, conn, username):
        while (True):
            try:
                data = Fernet(KEY).decrypt(conn.recv(BUFFER))
                print(f"{username[0]}: {str(data, 'utf-8')}")

                for connection in self.connections:
                    connection.send(Fernet(KEY).encrypt(bytes(f"({username[0]}): {data.decode()}", "utf-8")))
                if not data:
                    raise Exception
            except:
                print(f"({str(username[0])}) has Disconnected")

                users.remove(username)
                self.connections.remove(conn); conn.close()

                for connection in self.connections: connection.send(Fernet(KEY).encrypt(bytes(f"[{username[0]}] has disconnected", "utf-8")))
                break

            finally:
                if (len(self.connections) == 0): users.clear()

    def getInfo(self, conn):
        while (True):
            choice = input()
            for user in users:
                table.add_row([user[0], user[1]])

            if (len(table._rows) == 0):
                print("-"*25 + "\n[!] No Clients Connected\n" + "-"*25)
            else:
                print(table)

            table.clear_rows()


    def run(self):
        global conn

        while (True):
            try:
                conn, address = self.objSocket.accept()

                conn.send(KEY)
                username = [str(Fernet(KEY).decrypt(conn.recv(BUFFER)), "utf-8")] + [address[0]]
                users.append(username)

                t = threading.Thread(target=self.handler, args=(conn, username))
                t.daemon = True
                t.start()

                t2 = threading.Thread(target=self.getInfo, args=(conn,))
                t2.daemon = True
                t2.start()

                for connection in self.connections:
                    connection.send(Fernet(KEY).encrypt(bytes(f"[{username[0]}] has connected", "utf-8")))

                self.connections.append(conn)
                print(f"({str(username[0])}) has Connected")

            except KeyboardInterrupt:
                print("\nConnection has been Terminated. All Clients Disconnected")
                exit(1)

            except Exception as e:
                print(f"[-] Error Accepting Connection\nError Message: ({e})")
                exit(1)

server = Server()
server.run()
