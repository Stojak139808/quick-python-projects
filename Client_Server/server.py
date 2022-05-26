'''
Basic implementation of a multithreaded server, each clinet can communicate with the server
asynchronously, which is send messages or files
'''

import socket, threading

class Client_thread(threading.Thread):

    def __init__(self,clientAddress,clientsocket):
        self.clientAddress = clientAddress
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        print ("New connection added: ", clientAddress)

    def run(self):
        print ("Connection from : ", self.clientAddress)
        msg = ''
        while True:
            data = self.csocket.recv(2048)
            msg = data.decode('UTF-16')

            if msg==chr(3) or msg=='':
                break

            if msg == chr(2):
                self.csocket.send(chr(2).encode('UTF-16'))
                file = self.csocket.recv(2048).decode('UTF-16')

                self.csocket.send(chr(2).encode('UTF-16'))

                size = int(self.csocket.recv(2048).decode('UTF-16'))
                print("Recieveing file ", file, " size: ", size)
                f = open("copy_" + file, "wb")

                tmp = 0
                while tmp <= size:
                    tmp += 1024
                
                size = tmp

                collected = 0
                data = None
                while collected < size:
                    data = self.csocket.recv(1024)
                    #print(data)
                    f.write(data)
                    collected += 1024
                    print(collected)
                f.close()
                print("Done.")
                msg = ''
            else:
                print ("from client", self.clientAddress, ": ", msg)
        print ("Client at ", self.clientAddress , " disconnected...")


class Server:
    def __init__(self, ip, PORT):
        self.LOCALHOST = ip
        self.PORT = PORT
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.LOCALHOST, self.PORT))

    def start(self):
        print("Server started")
        print("Waiting for client request..")
        while True:
            self.server.listen(1)
            clientsock, clientAddress = self.server.accept()
            newthread = Client_thread(clientAddress, clientsock)
            newthread.start()


def main():
    serv = Server("127.0.0.1", 8080)
    serv.start()

if __name__ == "__main__":
    main()
