# Standard Libraries
import socket
import threading
import os
import time

HOST = "0.0.0.0"
PORT = 10000
bufsize = 0x400
users = []

os.system("clear" if os.name == "posix" else "cls")

def recvall(buffer):
    data = b""
    while (len(data) < buffer):
        data += conn.recv(buffer)
    return data

# Main Server System
class Server:
    objSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    objSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connections = []

    def __init__(self):
        self.objSocket.bind((HOST, PORT))
        self.objSocket.listen(socket.SOMAXCONN)
        print("(Listening for Incoming Connections)\n" + "-"*36)

    def handler(self, conn, username):
        while (True):
            try:
                data = conn.recv(bufsize)
                if (data.decode() == "SENDING-FILE"):
                    FileName = conn.recv(bufsize).decode(); FileSize = int(conn.recv(bufsize))
                    data = b"FILE-SENDING"

                for connection in self.connections:
                    connection.send(bytes(f"({username}): {data.decode()}", "utf-8"))
                if not data:
                    raise Exception
            except:
                print(f"({str(username)}) has Disconnected")

                users.remove(username)
                self.connections.remove(conn); conn.close(); time.sleep(1)
                break

            finally:
                if (len(self.connections) == 0):
                    users.clear(); time.sleep(2)

                    os.system("clear" if os.name == "posix" else "cls")
                    print("<No Clients in Chat>")

    def run(self):
        global conn

        while (True):
            try:
                conn, address = self.objSocket.accept()

                username = conn.recv(bufsize).decode()
                users.append(username)

                thread = threading.Thread(target=self.handler, args=(conn, username))
                thread.daemon = True; thread.start()

                self.connections.append(conn)
                print(f"({str(username)}) has Connected")

            except KeyboardInterrupt:
                print("\n[ Connection Terminated, All Clients Disconnected ]")
                exit()

            except (socket.error, Exception) as e:
                print(f"[ Error Accepting Connection ]\nError Message: ({e})")
                exit()

server = Server()
server.run()
