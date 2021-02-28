# Standard Libraries
import socket
import threading
import time
import os

# Connection Properties
HOST = "0.0.0.0"
PORT = 10000
buffer = 1024

users = []
conn = None

os.system("clear" if os.name == "posix" else "cls")

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
                data = conn.recv(buffer)
                print(f"{username}: " + data.decode())
                for connection in self.connections:
                    connection.send(bytes(f"({username}): {data.decode()}|" + " ".join(users), "utf-8"))
                if not data:
                    raise Exception
            except:
                print(f"({str(username)}) has Disconnected")

                users.remove(username)
                self.connections.remove(conn); conn.close()

                for connection in self.connections:
                    connection.send(bytes(f"[{username}] has disconnected", "utf-8"))

                break

            finally:
                if (len(self.connections) == 0):
                    users.clear(); time.sleep(2)

                    os.system("clear" if os.name == "posix" else "cls")
                    print("<No Users in Chat>")

    def run(self):
        global conn

        while (True):
            try:
                conn, address = self.objSocket.accept()

                username = conn.recv(buffer).decode()
                users.append(username)

                thread = threading.Thread(target=self.handler, args=(conn, username))
                thread.daemon = True; thread.start()

                for connection in self.connections:
                    connection.send(bytes(f"[{username}] has connected", "utf-8"))

                self.connections.append(conn)
                print(f"({str(username)}) has Connected")

            except KeyboardInterrupt:
                print("\nConnection has been Terminated. All Clients Disconnected")
                exit(1)

            except Exception as e:
                print(f"[-] Error Accepting Connection\nError Message: ({e})")
                exit(1)

server = Server()
server.run()
